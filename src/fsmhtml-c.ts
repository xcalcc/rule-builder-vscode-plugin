/*
   Copyright (C) 2019-2022 Xcalibyte (Shenzhen) Limited.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as os from "./lib/os"
import { strict } from 'assert';
import { release } from 'os';
export class FsmHtmlC {
    private ruleList: any = {};
    private fsmList: any = new Set();
    private fileUrl: string = "" //.rule 文件路径
    private baseUrl: string = "" //
    private ruleJsonUrl: string = "" //fsm 路径url
    private dataListUrl: string = "" //urul路径
    private rulesUrl: string = "" //file path of rules_en.json
    private rulesCnUrl: string = "" //file path of rules_cn.json
    private pathMsgUrl: string = "" //file path of pathMessageInternal.json
    private pathMessageUrl: string = "" //file path of path-msg.json
    private counterUrl: string = "" //file path of counter.json
    private relevantUrl: string = "" //folder path of relevant_files folder
    private dataListJson: any[] = []  //urule数据
    private rulesJson: any = {};
    private rulesChineseJson: any[] = [];
    private messageTemplateUrl: string = "";
    private extensionPath: string = '' //当前文件路径
    private sys: boolean = false  //判断系统
    private arrlistUrl: any[] = [] //c的数据
    constructor(private context: vscode.ExtensionContext) {
        if (vscode.workspace && vscode.workspace.workspaceFolders?.length) {
            this.sys = os.isWindows();
            this.baseUrl = vscode.workspace.workspaceFolders[0].uri.path;
            if (!this.sys) {
            } else {
                this.baseUrl = this.baseUrl.replace('/', '');
            }
            this.fileUrl = `${this.baseUrl}/.rule`;
            this.ruleJsonUrl = `${this.fileUrl}/fsm.json`
            this.dataListUrl = `${this.fileUrl}/dataList.json`
            this.relevantUrl = `${this.fileUrl}/relevant_files`
            this.rulesUrl = `${this.relevantUrl}/rules_en.json`
            this.rulesCnUrl = `${this.relevantUrl}/rules_cn.json`
            this.pathMsgUrl = `${this.fileUrl}/pathMessageInternal.json`
            this.pathMessageUrl = `${this.relevantUrl}/path-msg.json`
            this.messageTemplateUrl = `${this.fileUrl}/messageTemplate.json`
            this.counterUrl = `${this.fileUrl}/counter.json`
        }
        context.subscriptions.push(vscode.commands.registerCommand('rulebuilders.fsmHtml-c', () => {
            this.extensionPath = context.extensionPath ? context.extensionPath : '';
            this.createFile()
            this.getRules()
            this.getDataList()
            let cfnList: any[] = this.getfnc()
            let panel: any = this.loadpage();
            panel.webview.html = this.getWebViewContent(context, 'topology_es5_c.html'); //加载html文件资源
            setTimeout(() => {
                panel.webview.postMessage({ ruleList: this.ruleList, type: 'ruleList', dataList: this.dataListJson, rules: this.rulesJson, cfnList: cfnList });
            }, 1000)
            panel.webview.onDidReceiveMessage(async (message: any) => {
                console.log(message)
                switch (message.command) {
                    case "createFs":
                        let relevantFunctions = this.searchFunctions(message)
                        panel.webview.postMessage({ fnlist: relevantFunctions, type: 'createFn' });
                        break;
                    case 'addUrule':
                        // Does partial input validation and then writes to the dataList.json and rules.json in createDataJson()
                        if (message.override === "" || message.isCustom === "") {
                            vscode.window.showErrorMessage('Please fill in first two question.');
                            panel.webview.postMessage({ type: 'addUrule', status: 'none' })
                            return
                        }
                        if (!message.name) {
                            vscode.window.showErrorMessage('Name Missing');
                            panel.webview.postMessage({ type: 'addUrule', status: 'none' })
                            return
                        } else if (!(this.fsmList.has(message.code)) && (message.isCustom === 'F') && (message.override === 'F')){
                            vscode.window.showErrorMessage('Rule Code not found from FSM Rule Name');
                            panel.webview.postMessage({ type: 'addUrule', status: 'none' })
                            return
                        } else if (!(this.fsmList.has("CD-" + message.code)) && (message.isCustom === 'T') && (message.override === 'F')) {
                            vscode.window.showErrorMessage('Rule Code not found from FSM Rule Name. You do not need to add CD- to rule code.');
                            panel.webview.postMessage({ type: 'addUrule', status: 'none' })
                            return
                        } else {
                            let rules: any = {}
                            rules.category = message.category
                            rules.mapping = message.mapping
                            rules.AutoSAR = message.AutoSAR
                            rules.misra_c = message.misra_c
                            rules.misra_cpp = message.misra_cpp
                            rules.GJB5369 = message.GJB5369
                            rules.GJB8114 = message.GJB8114
                            rules.language = message.language
                            rules.msg_templ_en = message.template
                            rules.msg_templ_cn = message.template_cn
                            if (message.isCustom === 'T') {
                                rules.code = "CD-" + message.code
                            } else {
                                rules.code = message.code
                            }
                            rules.isCustom = message.isCustom
                            rules.override = message.override
                            rules.master_id = message.ids
                            rules.name = message.name
                            rules.name_cn = message.name_cn
                            rules.severity = message.severity
                            rules.compliance = message.compliance
                            rules.likelihood = message.likelihood
                            rules.cost = message.remediation
                            rules.desc_en = message.description
                            rules.desc_cn = message.description_cn
                            rules.abstract = message.abstract
                            rules.explanation = message.explanation
                            rules.abstract_cn = message.abstract_cn
                            rules.explanation_cn = message.explanation_cn
                            rules.example_good = message.example_good
                            rules.example_bad = message.example_bad
                            rules.details_en = "#### Abstract\n" + message.abstract + "\n\n#### Explanation\n" + message.explanation
                            rules.details_cn = "#### 概要\n" + message.abstract_cn + "\n\n#### 解释\n" + message.explanation_cn
                            let objExample: any = {}
                            objExample.good = this.extractExamples(message.example_good)
                            objExample.bad = this.extractExamples(message.example_bad)
                            rules.examples = objExample

                            let obj: any = {}
                            obj.name = message.name

                            if (message.isCustom === 'T') {
                                obj.code = "CD-" + message.code
                            } else {
                                obj.code = message.code
                            }

                            obj.rules = rules
                            obj.id = message.id ? message.id : new Date().getTime()
                            let type = message.id ? 'edit' : 'add'
                            console.log(obj)
                            this.createDataJson(obj, panel, type)
                        }
                        break;
                    case 'del':
                        this.delRule(message, panel)
                        break;
                    case 'delURule':
                        this.delURule(message, panel)
                        break;
                    // message to save the FSM in html file handled here
                    case 'save':
                        if (!message.name) {
                            vscode.window.showErrorMessage('请输入fsmName');
                            return
                        } else {
                            this.saveRule(message, panel)
                        }
                        break;
                    case 'edit':
                        this.editRule(message, panel)
                        break;
                    case 'shell':
                        this.toShell(message)
                        break;
                    case 'test':
                        // let mes: any = message
                        break;
                    case 'debug':
                        console.log(message.dataList)
                        break;
                    case 'openMi':
                        this.openMi(message)
                        break;
                    }
            }, undefined, context.subscriptions);
        }));
    }

    loadpage() {
        return vscode.window.createWebviewPanel(
            'htmlWebview', // viewType
            "ruleBuliders", // 视图标题
            vscode.ViewColumn.One, // 显示在编辑器的哪个部位
            {
                enableScripts: true, // 启用JS，默认禁用
                retainContextWhenHidden: true // webview被隐藏时保持状态，避免被重置
            }
        );
    }

    extractExamples(example_good: String) {
        let goodExample = {"cpp": [""], "java": [""], "c": [""], "general": [""]}
        var i = 0;
        while (i < example_good.length - 1) {
            if (example_good.substring(i, i + 3) === "///") {
                if (example_good.substring(i + 3, i + 7) === "cpp:") {
                    var startCharacter = i + 7;
                    i = i + 7;
                    while (i < example_good.length) {
                        if (example_good.substring(i, i + 3) === "///") {
                            goodExample["cpp"] = [example_good.substring(startCharacter, i)]
                            break
                        } else if (i === example_good.length - 1) {
                            goodExample["cpp"] = [example_good.substring(startCharacter, i + 1)]
                            break
                        } else {
                            i++;
                        }
                    }
                } else if (example_good.substring(i + 3, i + 8) === "java:") {
                    startCharacter = i + 8
                    i = i + 8
                    while (i < example_good.length) {
                        if (example_good.substring(i, i + 3) === "///") {
                            goodExample["java"] = [example_good.substring(startCharacter, i)]
                            break
                        } else if (i === example_good.length - 1) {
                            goodExample["java"] = [example_good.substring(startCharacter, i + 1)]
                            break
                        } else {
                            i++;
                        }
                    }

                } else if (example_good.substring(i + 3, i + 5) === "c:") {
                    startCharacter = i + 5
                    i = i + 5
                    while (i < example_good.length) {
                        if (example_good.substring(i, i + 3) === "///") {
                            goodExample["c"] = [example_good.substring(startCharacter, i)]
                            break
                        } else if (i === example_good.length - 1) {
                            goodExample["c"] = [example_good.substring(startCharacter, i + 1)]
                            break
                        } else {
                            i++;
                        }
                    }
                } else if (example_good.substring(i + 3, i + 11) === "general:") {
                    startCharacter = i + 13
                    i = i + 13
                    while (i < example_good.length) {
                        if (example_good.substring(i, i + 3) === "///") {
                            goodExample["general"] = [example_good.substring(startCharacter, i)]
                            break
                        } else if (i === example_good.length - 1) {
                            goodExample["general"] = [example_good.substring(startCharacter, i + 1)]
                            break
                        } else {
                            i++;
                        }
                    }
                } else {
                    vscode.window.showErrorMessage('Input Type Incorrect')
                    break;
                }
            } else {
                vscode.window.showErrorMessage('Input Type Incorrect')
                break;
            }
        }

        return goodExample
    }

    getWebViewContent(context: any, templatePath: string) {
        // console.log(context)
        // console.log(templatePath)
        const resourcePath = path.join(context.extensionPath, templatePath);
        const dirPath = path.dirname(resourcePath);
        let html = fs.readFileSync(resourcePath, 'utf-8');
        html = html.replace(/(<link.+?href="|<script.+?src="|<img.+?src=")(.+?)"/g, (m, $1, $2) => {
            return $1 + vscode.Uri.file(path.resolve(dirPath, $2)).with({ scheme: 'vscode-resource' }).toString() + '"';
        });
        return html;
    }
    //创建。rule文件夹
    createFile(): void {
        let checkDir = fs.existsSync(this.fileUrl);
        if (checkDir) {
            return
        }
        fs.mkdir(this.fileUrl, "0777", function (err) {
            if (err) {
                console.log(err);
            } else {
                console.log("creat done!");
            }

        })
    }
    //获取历史rules数据
    getRules(): void {
        let checkDir = fs.existsSync(this.ruleJsonUrl);
        if (checkDir) {
            let data = fs.readFileSync(this.ruleJsonUrl, 'utf-8');
            this.ruleList = JSON.parse(data)
        } else {
            this.ruleList = {}
        }
    }
    //获取dataList数据
    getDataList(): void {
        let checkDir = fs.existsSync(this.dataListUrl);
        if (checkDir) {
            let data = fs.readFileSync(this.dataListUrl, 'utf-8');
            this.dataListJson = JSON.parse(data)
        } else {
            this.dataListJson = []
        }
    }

    //编辑rule数据
    editRule(message: any, panel: any): void {
        let miFileUrl = `${this.relevantUrl}/${message.name}.mi`
        fs.readFile(this.ruleJsonUrl, 'utf-8', (err, data) => {
            if (data) {
                let newData = JSON.parse(data)
                let fsmcurrent = newData[message.name]
                panel.webview.postMessage({ fsmcurrent: fsmcurrent, type: 'refresh', miFileUrl: miFileUrl });
            }
        })
    }

    //删除rule 数据
    delRule(message: any, panel: any): void {
        fs.readFile(this.ruleJsonUrl, 'utf-8', (err, data) => {
            if (data) {
                let newData = JSON.parse(data)
                delete newData[message.name]
                let miFileUrl = `${this.relevantUrl}/${message.name}.mi`
                panel.webview.postMessage({ ruleList: newData, type: 'del', miFileUrl: miFileUrl, name: message.name, filePath: this.relevantUrl});
                message.text = newData
                this.saveRule(message, panel)
            }
        })
    }

    //Saves the FSM and writes the .mi file in the createMi() 
    saveRule(message: any, panel: any): void {
        let obj: any = {}
        let fsmJson: JSON 
        let miFileUrl = ""
        switch (message.type) {
            case 'del':
                obj = message.text
                let url = `${this.relevantUrl}/${message.name}.mi`
                this.deleteFolderRecursive(url)
                fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                this.fsmList.delete(message.name);
                break;
            case 'add':
                fsmJson = message.text
                this.createMi(fsmJson, message, false) //创建规则mi
                miFileUrl = `${this.relevantUrl}/${message.name}.mi`
                fs.readFile(this.ruleJsonUrl, 'utf-8', (err, data) => {
                    if (data) {
                        let newData = JSON.parse(data)
                        obj = newData;
                        obj[message.name] = fsmJson
                        fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                            if (err) { err.status(500).send('Server is error...') }
                        })
                    } else if (err && err.code == 'ENOENT') {
                        obj[message.name] = fsmJson
                        fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                            if (err) { err.status(500).send('Server is error...') }
                        })
                    }
                    panel.webview.postMessage({ ruleList: obj, type: 'ruleList', miFileUrl: miFileUrl, filePath: this.relevantUrl});
                    this.fsmList.add(message.name);
                })
                break;
            case 'addCustom':
                fsmJson = message.text
                message.name = "CD-" + message.name
                this.createMi(fsmJson, message, true) //创建规则mi
                miFileUrl = `${this.relevantUrl}/CD-${message.name}` 
                fs.readFile(this.ruleJsonUrl, 'utf-8', (err, data) => {
                    if (data) {
                        let newData = JSON.parse(data)
                        obj = newData;
                        obj[message.name] = fsmJson
                        fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                            if (err) { err.status(500).send('Server is error...') }
                        })
                    } else if (err && err.code == 'ENOENT') {
                        obj[message.name] = fsmJson
                        fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                            if (err) { err.status(500).send('Server is error...') }
                        })
                    }
                    panel.webview.postMessage({ ruleList: obj, type: 'ruleList', miFileUrl: miFileUrl, filePath: this.relevantUrl });
                    this.fsmList.add(message.name);
                })
                break;
            default:
                break;

        }

    }
    //删除文件
    deleteFolderRecursive(url: string) {
        fs.unlink(url, function (err) {
            if (err) {
                //  res.send("删除失败");
                return;
            }
        });
    }

    // creates the .mi file from FSM data.  Main work done in fliter()
    createMi(fsmJson: JSON, message: any, isCustom: boolean): void {
        let urls = `${this.relevantUrl}/${message.name}.mi`
        let jsdata = this.fliter(fsmJson, isCustom)
        fs.writeFile(urls, jsdata, (err: any) => {
            if (err) { }
        })
    }

    // main work to make the .mi done here
    fliter(obj: any, isCustom: boolean) {
        let str = ''
        let DEF_ACTION = ''
        let DECLARE = ''
        let allArr = obj.pens || []
        let nodeList = allArr.filter((item: any) => item.type == 0) || []
        let lines = allArr.filter((item: any) => item.type == 1) || []

        let messageTemplateComponents: any = {}
        let errorComponents: any = []

        const fs = require('fs')
        let messageTemplateFile = fs.readFileSync(this.messageTemplateUrl)
        let messageTemplate = JSON.parse(messageTemplateFile)

        nodeList.forEach((item: any) => {
            str += `NODE|${item.text}\n`
        });
        lines.forEach((item: any) => {
            let txt = item.text
            let arr = txt.includes("|") ? txt.split("|") : []
            let from = allArr.filter((it: any) => item.from.id == it.id)
            let to = allArr.filter((it: any) => item.to.id == it.id)
    
            // Declare not needed, so commented out
            /* let remarkArr = this.dataListJson.filter((it: any) => it.name == arr[1])
            DECLARE += `DECLARE|${arr[1]}|CUSTOM|${remarkArr.length ? remarkArr[0].remark : ''}\n` */

            const fs = require('fs')
            let messageIdFile = fs.readFileSync(this.pathMsgUrl)
            let pathMessageList = JSON.parse(messageIdFile)
            let messageIdPosition = arr.length - 1;
            let id = 0
            if (arr[messageIdPosition] in pathMessageList) {
                id = pathMessageList[arr[messageIdPosition]]
            } else {
                let counterFile = fs.readFileSync(this.counterUrl)
                let stuff = JSON.parse(counterFile)
                id = stuff["counter"]
                pathMessageList[arr[messageIdPosition]] = id
                stuff["counter"] = stuff["counter"] + 1
                fs.writeFileSync(this.counterUrl, JSON.stringify(stuff, null, "\t"), 'utf-8')
            }

            // All parameters inputed
            if (arr.length == 5) {
                if (isCustom === false) {
                    str += `EDGE|${from[0]['text']}|${to[0]['text']}|${arr[0]}|${arr[1]}|${arr[2]}|${arr[3]}|` + id + '\n'
                } else {
                    str += `EDGE|${from[0]['text']}|${to[0]['text']}|${arr[0]}|${arr[1]}|${arr[2]}|CD-${arr[3]}|` + id + '\n'
                }
                
            } else if (arr.length == 2) {
                // Input character '~' to indicate default action
                if (txt[0] == '~') {
                    if (isCustom === false) {
                        DEF_ACTION += `DEF_ACTION|${from[0]['text']}|${arr[0].substring(1)}|` + id + '\n'
                    } else {
                        DEF_ACTION += `DEF_ACTION|${from[0]['text']}|CD-${arr[0].substring(1)}|` + id + '\n'
                    }
                } else {
                    // Only function and message ID inputed
                    str += `EDGE|${from[0]['text']}|${to[0]['text']}|${arr[0]}|none|none|none|` + id + '\n'
                }
            } else {
                // Any other invalid input type not following the above structure
                throw 'INPUT IS INVALID.  PLEASE INPUT AGAIN.'
            }

            let pathMessages = []
            for (const [key, value] of Object.entries(pathMessageList)) {
                pathMessages.push({ "id": `${value}`, "msg_cn": `${key}`, "msg_en": `${key}`})
            }

            fs.writeFileSync(this.pathMsgUrl, JSON.stringify(pathMessageList, null, "\t"), 'utf-8')
            fs.writeFileSync(this.pathMessageUrl, JSON.stringify(pathMessages, null, "\t"), 'utf-8')
        })

        lines.forEach((item: any) => {
            let txt = item.text
            let arr = txt.includes("|") ? txt.split("|") : []
            let from = allArr.filter((it: any) => item.from.id == it.id)
            let to = allArr.filter((it: any) => item.to.id == it.id)

            // Declare not needed, so commented out
            /* let remarkArr = this.dataListJson.filter((it: any) => it.name == arr[1])
            DECLARE += `DECLARE|${arr[1]}|CUSTOM|${remarkArr.length ? remarkArr[0].remark : ''}\n` */

            // All parameters inputed
            if (arr.length == 5) {
                let pair = [`${from[0]['text']}`, `${to[0]['text']}`]
                if (arr[3] !== "none" || arr[3].replace(" ", "") !== "") {
                    errorComponents.push(pair)
                } 

                messageTemplateComponents.pair = this.composeMessageTemplateComponent(`${from[0]['text']}`, `${to[0]['text']}`, arr[4])

            } else if (arr.length == 2) {
                // Input character '~' to indicate default action
                if (txt[0] == '~') {
                    let pair = [`${from[0]['text']}`, `${to[0]['text']}`]
                    if (arr[0] !== "none" || arr[0].replace(" ", "") !== "") {
                        errorComponents.push(pair)
                    }

                    messageTemplateComponents.pair = this.composeMessageTemplateComponent(`${from[0]['text']}`, `${to[0]['text']}`, arr[0])
                }
            } 

        })

        return `${str}${DEF_ACTION}`

        // return `${str}${DEF_ACTION}${DECLARE}`
    }

    
    composeMessageTemplateComponent(from: String, to: String, pathMessage: String) : String {
        if (from.toLowerCase() === "start") {
            return ("In file ${so.filename}, the function ${so.func} in line ${so.line} caused " + pathMessage + ". ")
        } else if (to.toLowerCase() === "end") {
            return ("In file ${ si.filename }, the function ${ si.func } in line ${ si.line } caused " + pathMessage + ". ")
        } else {
            return ("Then, " + pathMessage + ". ")
        }
    }


    checkConditions(text: String) : String {
        text.replace(/\s/g, "");

        for (var i = 0; i < text.length - 1; i++) {
            var first = text.charAt(i);
            var second = text.charAt(i + 1);

            if (first === '&' && second === '&') {
                text
            }
        }

        return ""
    }

    //删除delURule
    delURule(message: any, panel: any): void {
        switch (message.type) {
            case "del":
                this.dataListJson = this.dataListJson.filter((item: any) => item.id != message.id)

                let rules: any = [];
                for (var i = 0; i < this.dataListJson.length; i++) {
                    let dataCopy = { ...this.dataListJson[i].rules };
                    delete dataCopy["name_cn"]
                    delete dataCopy["desc_cn"]
                    delete dataCopy["AutoSAR"]
                    delete dataCopy["misra_c"]
                    delete dataCopy["misra_cpp"]
                    delete dataCopy["GJB5369"]
                    delete dataCopy["GJB8114"]
                    delete dataCopy["msg_templ_cn"]
                    delete dataCopy["details_cn"]
                    delete dataCopy["abstract"]
                    delete dataCopy["explanation"]
                    delete dataCopy["abstract_cn"]
                    delete dataCopy["explanation_cn"]
                    delete dataCopy["example_good"]
                    delete dataCopy["example_bad"]
                    delete dataCopy["isCustom"]
                    delete dataCopy["override"]

                    dataCopy['msg_templ'] = dataCopy["msg_templ_en"]
                    delete dataCopy["msg_templ_en"]
                    dataCopy['desc'] = dataCopy["desc_en"]
                    delete dataCopy["desc_en"]
                    dataCopy['details'] = dataCopy["details_en"]
                    delete dataCopy["details_en"]
                    


                    rules.push(dataCopy);
                }
                let outputEnglish = rules;

                let rulesChinese = [];
                for (var i = 0; i < this.dataListJson.length; i++) {
                    let dataCopy2 = { ...this.dataListJson[i].rules };
                    delete dataCopy2["name"]
                    delete dataCopy2["desc_en"]
                    delete dataCopy2["AutoSAR"]
                    delete dataCopy2["misra_c"]
                    delete dataCopy2["misra_cpp"]
                    delete dataCopy2["GJB5369"]
                    delete dataCopy2["GJB8114"]
                    delete dataCopy2["msg_templ_en"]
                    delete dataCopy2["details_en"]
                    delete dataCopy2["abstract"]
                    delete dataCopy2["explanation"]
                    delete dataCopy2["abstract_cn"]
                    delete dataCopy2["explanation_cn"]
                    delete dataCopy2["example_good"]
                    delete dataCopy2["example_bad"]
                    delete dataCopy2["isCustom"]
                    delete dataCopy2["override"]

                    dataCopy2['msg_templ'] = dataCopy2["msg_templ_cn"]
                    delete dataCopy2["msg_templ_cn"]
                    dataCopy2['name'] = dataCopy2["name_cn"]
                    delete dataCopy2["name_cn"]
                    dataCopy2['desc'] = dataCopy2["desc_cn"]
                    delete dataCopy2["desc_cn"]
                    dataCopy2['details'] = dataCopy2["details_cn"]
                    delete dataCopy2["details_cn"]
                    

                    rulesChinese.push(dataCopy2);
                }
                let outputChinese = rulesChinese;

                fs.writeFile(this.dataListUrl, JSON.stringify(this.dataListJson, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                fs.writeFile(this.rulesUrl, JSON.stringify(outputEnglish, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                fs.writeFile(this.rulesCnUrl, JSON.stringify(outputChinese, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                panel.webview.postMessage({ type: 'addUrule', status: 'no', dataList: this.dataListJson, rules: this.rulesJson })
                break;
        }
    }

    //OLD FUNCTION
    /* createDataJson(obj: any, panel: any, type: any): void {
        let dataArr: any[] = []
        fs.readFile(this.dataListUrl, 'utf-8', (err, data) => {
            if (data) {
                let newData = JSON.parse(data)
                if (type == 'add') {
                    dataArr = [...newData, obj]
                } else {
                    let currentIdIndex = newData.findIndex((item: any) => item.id == obj.id);
                    newData.splice(currentIdIndex, 1, obj)
                    dataArr = [...newData]
                }
                fs.writeFile(this.dataListUrl, JSON.stringify(dataArr, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                this.convertJson();
                // this.runJsonConversionScript('./convertJson.js')
            } else if (err && err.code == 'ENOENT') {
                dataArr.push(obj)
                fs.writeFile(this.dataListUrl, JSON.stringify(dataArr, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                this.convertJson();
                // this.runJsonConversionScript('./convertJson.js')
            }
            this.dataListJson = dataArr
            panel.webview.postMessage({ type: 'addUrule', status: 'yes', dataList: dataArr })
        })
    } */

    //urule 数据
    createDataJson(obj: any, panel: any, type: any): void {
        let dataArr: any[] = []
        let outputEnglish: any[] = []
        let outputChinese: any[] = []
        console.log(obj)

        fs.readFile(this.dataListUrl, 'utf-8', (err, data) => {
            if (data) {
                let newData = JSON.parse(data)
                if (type == 'add') {
                    dataArr = [...newData, obj]
                } else {
                    let currentIdIndex = newData.findIndex((item: any) => item.id == obj.id);
                    newData.splice(currentIdIndex, 1, obj)
                    dataArr = [...newData]
                }

                let rules = [];

                for (var i = 0; i < dataArr.length; i++) {
                    let dataCopy = { ...dataArr[i].rules };
                    delete dataCopy["name_cn"]
                    delete dataCopy["desc_cn"]
                    delete dataCopy["AutoSAR"]
                    delete dataCopy["misra_c"]
                    delete dataCopy["misra_cpp"]
                    delete dataCopy["GJB5369"]
                    delete dataCopy["GJB8114"]
                    delete dataCopy["msg_templ_cn"]
                    delete dataCopy["details_cn"]
                    delete dataCopy["abstract"]
                    delete dataCopy["explanation"]
                    delete dataCopy["abstract_cn"]
                    delete dataCopy["explanation_cn"]
                    delete dataCopy["example_good"]
                    delete dataCopy["example_bad"]
                    delete dataCopy["isCustom"]
                    delete dataCopy["override"]

                    dataCopy['msg_templ'] = dataCopy["msg_templ_en"]
                    delete dataCopy["msg_templ_en"]
                    dataCopy['desc'] = dataCopy["desc_en"]
                    delete dataCopy["desc_en"]
                    dataCopy['details'] = dataCopy["details_en"]
                    delete dataCopy["details_en"]


                    rules.push(dataCopy);
                }
                let outputEnglish = rules

                let rulesChinese = [];
                for (var i = 0; i < dataArr.length; i++) {
                    let dataCopy2 = { ...dataArr[i].rules };
                    delete dataCopy2["name"]
                    delete dataCopy2["desc_en"]
                    delete dataCopy2["AutoSAR"]
                    delete dataCopy2["misra_c"]
                    delete dataCopy2["misra_cpp"]
                    delete dataCopy2["GJB5369"]
                    delete dataCopy2["GJB8114"]
                    delete dataCopy2["msg_templ_en"]
                    delete dataCopy2["details_en"]
                    delete dataCopy2["abstract"]
                    delete dataCopy2["explanation"]
                    delete dataCopy2["abstract_cn"]
                    delete dataCopy2["explanation_cn"]
                    delete dataCopy2["example_good"]
                    delete dataCopy2["example_bad"]
                    delete dataCopy2["isCustom"]
                    delete dataCopy2["override"]

                    dataCopy2['msg_templ'] = dataCopy2["msg_templ_cn"]
                    delete dataCopy2["msg_templ_cn"]
                    dataCopy2['name'] = dataCopy2["name_cn"]
                    delete dataCopy2["name_cn"]
                    dataCopy2['desc'] = dataCopy2["desc_cn"]
                    delete dataCopy2["desc_cn"]
                    dataCopy2['details'] = dataCopy2["details_cn"]
                    delete dataCopy2["details_cn"]


                    rulesChinese.push(dataCopy2);
                }
                let outputChinese = rulesChinese

                fs.writeFile(this.dataListUrl, JSON.stringify(dataArr, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })

                fs.writeFile(this.rulesUrl, JSON.stringify(outputEnglish, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })

                fs.writeFile(this.rulesCnUrl, JSON.stringify(outputChinese, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })

            } else if (err && err.code == 'ENOENT') {
                vscode.window.showErrorMessage('Encountered error ENOENT.  Cannot create or update JSON successfully.');
            }
            this.dataListJson = dataArr
            this.rulesJson = outputEnglish;
            this.rulesChineseJson = outputChinese;
            panel.webview.postMessage({ type: 'addUrule', status: 'yes', dataList: dataArr })
        })
    }

    //执行脚本
    toShell(message: any): void {
        let readFile = fs.readFileSync(this.rulesUrl, 'utf-8')
        let arr = JSON.parse(readFile).rules
        if (arr === null){
            vscode.window.showErrorMessage('Issue reading rules json file.') 
            return
        }
        let check = this.validateRuleDetailInput(arr)
        if (check === false) {
            return;
        }
        let terminalB: any = vscode.window.createTerminal({ name: "createFn" });
        terminalB.show(true);
        let serverIp: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.serverIp');
        let serverUseName: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.serverUseName');
        let serverPasswd: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.serverPasswd');
        let newFileUrl: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.fileUrl');
        let databasePort: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.databasePort');
        let databaseUser: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.databaseUser');
        let databasePassword: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.databasePassword');
        let mainpyUrl: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.mainpyUrl');
        let tarGetUrl: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.tarGetUrl');
        let XVSA_PATH: any = vscode.workspace.getConfiguration().get('rulebuild.exceptions.file.extensions.xvsaUrl');
        let newfile: string = `${this.relevantUrl}/${message.name}.mi`
        let fileNames: string = `${newFileUrl}/${message.name}.mi`
        let configFlie: string = `${newFileUrl}/config.ini`
        let rules: any = []
        this.dataListJson.forEach((item: any) => {
            rules.push({ rulecode: item.name, "ruleset": "CUSTOM", "description": item.remark, "name": item.remark })
        })
        let strConfig: string = `[config]\nname = "${message.name}"\nlang = "java"\nxvsa_path="${XVSA_PATH}"\ninput = "${fileNames}"\nreferences = ""\ndependency = ""\nhost = "${serverIp}"\nuser = "${databaseUser}"\nport = "${databasePort}"\npassword="${databasePassword}"\nrules=${JSON.stringify(rules)}\ntarget = "${tarGetUrl}"`
        let confUrl: string = `${this.fileUrl}/config.ini`
        fs.writeFile(confUrl, strConfig, 'utf-8', (err: any) => {
            if (err) { err.status(500).send('Server is error...') }
        })
        let filLis: any = [newfile, confUrl]
        let fileNameArr: any = [fileNames, configFlie]
        let pytest: any = ''

        if (!this.sys) {
            pytest = `${this.extensionPath}/test.py`
        } else {
            pytest = `${this.extensionPath}\\test.py`
        }
        terminalB.sendText('cmd'); //输入命令
        //terminalB.sendText(`python ${pytest} ${serverUseName} ${serverPasswd} ${serverIp} ${filLis} ${fileNameArr} ${mainpyUrl} ${tarGetUrl} ${newFileUrl}`)
    }
    //获取函数集
    getfnc() {
        let cFunctionUrl = `${this.fileUrl}/cFunction.json`
        let checkDir = fs.existsSync(cFunctionUrl);
        if (checkDir) {
            let cfnList = fs.readFileSync(cFunctionUrl, 'utf-8');
            return JSON.parse(cfnList)
        } else {
            return []
        }
    }

    //获取程文件
    getAll(level: any, dir: any) {
        let filesNameArr: any[] = []
        let arrlistUrl: any[] = []
        let cur = 0
        // 用个hash队列保存每个目录的深度
        let mapDeep: any = {}
        mapDeep[dir] = 0
        // 先遍历一遍给其建立深度索引
        function getMap(dir: any, curIndex: any) {
            let files = fs.readdirSync(dir) //同步拿到文件目录下的所有文件名
            files.map(function (file) {
                //var subPath = path.resolve(dir, file) //拼接为绝对路径
                let subPath = path.join(dir, file) //拼接为相对路径
                let stats = fs.statSync(subPath) //拿到文件信息对象
                // 必须过滤掉node_modules文件夹
                if (file != 'node_modules') {
                    mapDeep[file] = curIndex + 1
                    if (stats.isDirectory()) { //判断是否为文件夹类型
                        return getMap(subPath, mapDeep[file]) //递归读取文件夹
                    }
                }
            })
        }
        getMap(dir, mapDeep[dir])
        function readdirs(dir: any, folderName: string, myroot?: any) {
            let result: any = {};
            result = { //构造文件夹数据
                path: dir,
                title: path.basename(dir),
                type: 'directory',
                deep: mapDeep[folderName]
            }
            let files = fs.readdirSync(dir) //同步拿到文件目录下的所有文件名
            result.children = files.map(function (file) {
                //var subPath = path.resolve(dir, file) //拼接为绝对路径
                let subPath = path.join(dir, file) //拼接为相对路径
                let stats = fs.statSync(subPath) //拿到文件信息对象
                if (stats.isDirectory()) { //判断是否为文件夹类型
                    return readdirs(subPath, file, file) //递归读取文件夹
                }
                if (subPath.endsWith('.c')) {
                    arrlistUrl.push(subPath)
                }
                return { //构造文件数据
                    path: subPath,
                    name: file,
                    type: 'file'
                }
            })
            return result //返回数据
        }
        filesNameArr.push(readdirs(dir, dir))
        this.arrlistUrl = arrlistUrl
        return filesNameArr
    }
    // /urule 数据
    createCfnJson(arr: any): void {
        let cFunctionUrl = `${this.fileUrl}/cFunction.json`
        fs.writeFile(cFunctionUrl, JSON.stringify(arr, null, "\t"), 'utf-8', (err: any) => {
            if (err) { err.status(500).send('Server is error...') }
        })
    }

    validateRuleDetailInput(arr: any): boolean {
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].language.replace(" ", "") === "") {
                vscode.window.showErrorMessage('Missing info on language for rule ' + arr[i].code)
                return false
            }

            if (arr[i].severity === "") {
                vscode.window.showErrorMessage('Missing info on severity for rule ' + arr[i].code)
                return false
            }

            if (arr[i].compliance === "") {
                vscode.window.showErrorMessage('Missing info on compliance for rule ' + arr[i].code)
                return false
            }

            if (arr[i].likelihood === "") {
                vscode.window.showErrorMessage('Missing info on likelihood for rule ' + arr[i].code)
                return false
            }

            if (arr[i].remediation === "") {
                vscode.window.showErrorMessage('Missing info on remediation cost for rule ' + arr[i].code)
                return false
            }

            let details = arr[i].details_cn 
            if (details === "#### ABSTRACT\n\n\n#### EXPLANATION\n" || details.includes("### ABSTRACT\n\n\n")) {
                vscode.window.showErrorMessage('Missing info on english details cost for rule ' + arr[i].code)
                return false
            }

            let details_cn = arr[i].details_cn
            if (details_cn === "#### 概要\n\n\n#### 解释\n" || details_cn.includes("### 概要\n\n\n")) {
                vscode.window.showErrorMessage('Missing info on chinese details cost for rule ' + arr[i].code)
                return false
            }


            let languages = arr[i].language
            languages = languages.replace(" ", "")
            languages = languages.replace("c++", "cpp")
            let languageList = languages.split(",")
            
            for (var j = 0; j < languageList.length; j++) {
                let good_example = arr[i].example.good[languageList[j]]
                let bad_example = arr[i].example.bad[languageList[j]]
                good_example.replace("\n", "")
                good_example.replace(" ", "")
                bad_example.replace("\n", "")
                bad_example.replace(" ", "")

                if (good_example === "") {
                    vscode.window.showErrorMessage('Missing info on good examples in ' + languageList[j] + ' for  ' + arr[i].code)
                    return false;
                }

                if (bad_example === "") {
                    vscode.window.showErrorMessage('Missing info on bad examples in ' + languageList[j] + ' for  ' + arr[i].code)
                    return false;
                }
            }
        }
        
        return true
    }

    searchFunctions(message: any) : any {
        let textToSearch = message.text
        if (textToSearch === null) {
            return null;
        }
        let relevantFunctions = []
        let data = fs.readFileSync(`${this.fileUrl}/cFunction.json`, 'utf-8');
        let functions = JSON.parse(data)

        for (var i = 0; i < functions.length; i++) {
            if (functions[i].includes(textToSearch)) {
                relevantFunctions.push(functions[i])
            }
        }
        
        return relevantFunctions
    }

    openMi(message : any) : any {
        let path = ".rule/relevant_files/" + message.rule + ".mi"
        let terminalB: any = vscode.window.createTerminal({ name: "openMi" });
        terminalB.sendText("open " + path)
    }
}