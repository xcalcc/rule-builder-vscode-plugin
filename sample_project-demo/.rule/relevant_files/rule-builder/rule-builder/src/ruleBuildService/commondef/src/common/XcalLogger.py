#
#  Copyright (C) 2019-2020  XC Software (Shenzhen) Ltd.
#


import json
import logging

from common import CommonGlobals

try:
    from opentracing import Format, tags
    from jaeger_client import Config, Span
    from jaeger_client.reporter import InMemoryReporter
except:
    CommonGlobals.use_jaeger = False
    logging.warning("Jaeger seems missing, skipping Jaeger initialization")

    class Span:
        pass


class XcalLogger(object):
    TRACE_LEVEL_DEBUG = 10
    TRACE_LEVEL_INFO = 20
    TRACE_LEVEL_WARNING = 30
    TRACE_LEVEL_ERROR = 40
    TRACE_LEVEL_FATAL = 50

    # Self defined level
    XCAL_TRACE_LEVEL = 25

    def __init__(self, service_name: str, func_name: str, parent=None, external:Span = None,
                 real_tracer: bool = False):
        self.name = service_name
        self.parent = parent
        self.func_name = func_name
        self.currentSpan = None
        self.trace_level = 0

        if CommonGlobals.use_jaeger and CommonGlobals.tracer is None and real_tracer is False:
            self.initialize_in_mem_tracer()

        if CommonGlobals.use_jaeger and CommonGlobals.old_tracer is None and real_tracer is True:
            self.initialize_real_tracer()

        if CommonGlobals.use_jaeger and isinstance(parent, XcalLogger):
            self.currentSpan = CommonGlobals.tracer.start_span(service_name + "." + func_name,
                                                               child_of=parent.currentSpan)
        elif CommonGlobals.use_jaeger and external is not None:
            self.currentSpan = CommonGlobals.tracer.start_span(service_name + "." + func_name, child_of=external)
        elif CommonGlobals.use_jaeger:
            self.currentSpan = CommonGlobals.tracer.start_span(service_name + "." + func_name)
        else:
            self.currentSpan = None

    def initialize_in_mem_tracer(self):
        """
         Initialize an in-memory tracer and then
        :return:
        """
        # May be used to disable jaeger
        if not CommonGlobals.use_jaeger:
            return

        if CommonGlobals.tracer is not None:
            if CommonGlobals.old_tracer is None:
                CommonGlobals.old_tracer = CommonGlobals.tracer
            else:
                return
            # Try to restart a tracer ?

        config = Config(
            config={  # usually read from some yaml config
                'reporter_batch_size': 3,
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'logging': True,
                'local_agent': {
                    'reporting_host': CommonGlobals.jaeger_agent_host,
                    'reporting_port': CommonGlobals.jaeger_agent_port
                },
            },
            service_name=CommonGlobals.jaeger_service_name,
            validate=True
        )

        # this call also sets opentracing.tracer
        CommonGlobals.tracer = config.initialize_tracer()

        if (CommonGlobals.tracer and
            CommonGlobals.tracer.reporter and
            CommonGlobals.tracer.reporter.reporters and
            len(CommonGlobals.tracer.reporter.reporters) < 3 and
            CommonGlobals.enable_memory_cache):
            # Setting up in-mem tracer, for later rerouting to the real server
            in_mem_rp = InMemoryReporter()
            CommonGlobals.tracer.reporter.reporters = CommonGlobals.tracer.reporter.reporters + (in_mem_rp,)

    def info(self, operation_name: str, message: any):
        logging.info(operation_name + " " + str(message))
        if self.currentSpan is not None:
            with CommonGlobals.tracer.start_span("%s-%s" % (self.name, self.func_name), child_of=self.currentSpan) as child_span:
                child_span.info(operation_name)
                child_span.info(message)
        else:
            self.report_jaeger_not_found()

    def error(self, service_name: str, func_name: str, message: any):
        logging.error((message, "in", func_name, "in", service_name))
        if self.currentSpan is not None:
            with CommonGlobals.tracer.start_span("%s" % func_name, child_of=self.currentSpan) as child_span:
                child_span.error("Error at %s, in func %s" % (service_name, func_name), message)
        else:
            self.report_jaeger_not_found()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.currentSpan is not None:
            self.currentSpan.__exit__(exc_type, exc_val, exc_tb)

    def finish(self):
        if self.currentSpan is not None:
            self.currentSpan.finish()

    def trace(self, operation_name: str, message: any):
        logging.log(XcalLogger.XCAL_TRACE_LEVEL, operation_name + " " + str(message))
        if self.currentSpan is not None:
            with CommonGlobals.tracer.start_span("%s-%s" % (self.name, self.func_name),
                                                 child_of=self.currentSpan) as child_span:
                child_span.info(operation_name)
                child_span.info(message)
        else:
            self.report_jaeger_not_found()

    def warn(self, operation_name: str, message: any):
        logging.warning(operation_name + " " + str(message))
        if self.currentSpan is not None:
            with CommonGlobals.tracer.start_span("%s-%s" % (self.name, self.func_name),
                                                 child_of=self.currentSpan) as child_span:
                child_span.info(operation_name)
                child_span.info(message)
        else:
            self.report_jaeger_not_found()

    def debug(self, operation_name: str, message: any):
        logging.debug(operation_name + " " + str(message))
        if self.currentSpan is not None:
            with CommonGlobals.tracer.start_span("%s-%s" % (self.name, self.func_name),
                                                 child_of=self.currentSpan) as child_span:
                child_span.info(operation_name)
                child_span.info(message)
        else:
            self.report_jaeger_not_found()

    def report_jaeger_not_found(self):
        # Do nothing in reporting Jaeger missing.
        pass

    def set_tag(self, key, value):
        if self.currentSpan is not None:
            self.currentSpan.set_tag(key, value)


class XcalLoggerExternalLinker(object):

    @staticmethod
    def prepare_server_span_scope_from_string(service_name:str, func_name:str, headers_string:str):
        """
        Read the injected info from the headers JSON string (e.g. from kafka)
        :param func_name:
        :param service_name:
        :param headers_string: A JSON-format string containing the info injected by prepare_client_request_headers()
        :return: XcalLogger for use
        """
        json_obj = json.loads(headers_string)
        return XcalLoggerExternalLinker.prepare_server_span_scope(service_name, func_name, json_obj)

    @staticmethod
    def prepare_server_span_scope(service_name:str, func_name:str, headers:dict):
        """
        Read the injected info from the headers (from HTTP request)
        :param func_name:
        :param service_name:
        :param headers:
        :return: XcalLogger for use
        """
        if not CommonGlobals.use_jaeger:
            return XcalLogger(service_name, func_name=func_name)

        logging.info("request.headers is %s", headers)
        span_ctx = CommonGlobals.tracer.extract(Format.HTTP_HEADERS, headers)
        logging.info("span_ctx is %s", span_ctx)
        if span_ctx is None:
            return XcalLogger(service_name, func_name=func_name)
        else:
            span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
            logging.info("span_tags is %s", span_tags)
            parent_span = CommonGlobals.tracer.start_span(
                service_name, child_of=span_ctx, tags=span_tags)
            return XcalLogger(service_name, func_name=func_name, external=parent_span)

    @staticmethod
    def prepare_client_request_headers(url, http_method, logger:XcalLogger, headers: dict = {}):
        """
        Write the Jaeger related info to the header region.
        :param url: api url
        :param http_method: post/get/xxx
        :param logger:
        :param headers:
        :return: request headers, or {} if jaeger is not used right now.
        """
        if not CommonGlobals.use_jaeger:
            return headers

        logging.info("jaeger_tracer object is %s", CommonGlobals.tracer)
        span = logger.currentSpan
        if span is None:
            return headers

        span.set_tag(tags.HTTP_METHOD, http_method)
        span.set_tag(tags.HTTP_URL, url)
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
        CommonGlobals.tracer.inject(span, Format.HTTP_HEADERS, headers)
        return headers

    @staticmethod
    def prepare_client_request_string(url, http_method, logger:XcalLogger):
        return json.dumps(XcalLoggerExternalLinker.prepare_client_request_headers(url, http_method, logger))