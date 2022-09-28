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
export class FsmHtmlJava {
    private ruleList: any = {};
    private fileUrl: string = "" //.rule 文件路径
    private baseUrl: string = "" //
    private ruleJsonUrl: string = "" //fsm 路径url
    private dataListUrl: string = "" //urul路径
    private timer = setInterval(function () { });//时间变量
    private dataListJson: any[] = []  //urule数据
    private fnsList: String[] = []  //函数集
    private extensionPath: string = '' //当前文件路径
    private tableMiUrl: string = ''  //vtable.mi 路径
    private tableMiName: string = '' //vtable.mi名字
    private jarUrl: string = '' //jar 路径
    private jarName: string = '' //jar名字
    private sys: boolean = false  //判断系统

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
        }
        context.subscriptions.push(vscode.commands.registerCommand('rulebuilders.fsmHtml-java', () => {
            this.extensionPath = context.extensionPath ? context.extensionPath : '';
            this.createFile()
            this.getRules()
            this.getDataList()
            this.getJarUrl()
            let panel = this.loadpage();
            panel.webview.html = this.getWebViewContent(context, 'topology_es5.html'); //加载html文件资源
            setTimeout(() => {
                panel.webview.postMessage({ ruleList: this.ruleList, type: 'ruleList', dataList: this.dataListJson, jarUrl: this.jarUrl, tableMiUrl: this.tableMiUrl }); //传送历史rules数据	
            }, 1000);
            this.getFnList(panel) //函数列
            panel.webview.onDidReceiveMessage(message => {
                switch (message.command) {
                    case "createFs":
                        this.createFn(panel)
                        break;
                    case 'edit':
                        this.editRule(message, panel)
                        break;
                    case 'del':
                        this.delRule(message, panel)
                        break;
                    case 'delURule':
                        this.delURule(message, panel)
                        break;
                    case 'addUrule':
                        if (!message.name) {
                            vscode.window.showErrorMessage('请输入ruleName');
                            panel.webview.postMessage({ type: 'addUrule', status: 'none' })
                            return
                        } else {
                            let obj: any = {}
                            obj.name = message.name
                            obj.abstract = message.abstract                           
                            obj.description = message.description
                            obj.severity = message.severity
                            obj.likelihood = message.likelihood
                            obj.remediation = message.remediation
                            obj.example_good = message.example_good
                            obj.example_bad = message.example_bad
                            obj.id = message.id ? message.id : new Date().getTime()
                            let type = message.id ? 'edit' : 'add'
                            this.createDataJson(obj, panel, type)
                        }
                        break;
                    case 'save':
                        if (!message.name) {
                            vscode.window.showErrorMessage('请输入fsmName');
                            return
                        } else {
                            this.saveRule(message, panel)
                        }
                        break;
                    case 'shell':
                        this.toShell(message)
                        break;
                    case 'test':
                        //	let testObj = message	
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
    getWebViewContent(context: any, templatePath: string) {
        console.log(context)
        console.log(templatePath)
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
    getJarUrl(): void {
        let miurl = `${this.baseUrl}/target`
        let checkDir = fs.existsSync(miurl)
        if (checkDir) {
            let files = fs.readdirSync(miurl);
            let urlArr = files.filter(item => item.includes('.jar'))
            if (urlArr.length) {
                this.jarName = urlArr[0]
                this.jarUrl = `${miurl}/${urlArr[0]}`
            } else {
                this.jarName = ''
                this.jarUrl = ''
            }
        }
    }
    getFnList(panel: any): void {
        let miurl = `${this.baseUrl}/target/xvsa-out`
        let checkDir = fs.existsSync(miurl);
        if (checkDir) {
            let files = fs.readdirSync(miurl);
            let dfv = files.filter(item => item.includes('vtable.mi'))
            if (dfv.length) {
                let miName = dfv[0]
                this.tableMiName = miName
                let newUl = `${miurl}/${miName}`
                this.tableMiUrl = newUl //赋值
                fs.readFile(newUl, 'utf-8', (err, data) => {
                    if (data) {
                        let miFlie = data.split("\n")
                        this.fnsList = miFlie
                        //packageGet(fnsList)
                        setTimeout(() => {
                            panel.webview.postMessage({ text: miFlie, type: 'fnList', tableMiUrl: this.tableMiUrl });
                        }, 1000)
                    }
                })
            }
        }
    }
    createFn(panel: any): void {
        let XVSA = process.env.XVSA_HOME || ''
        let terminalA = vscode.window.createTerminal({ name: "createFn" });
        terminalA.show(true);
        let cmds = "";
        if (!!this.sys) {
            terminalA.sendText('cmd'); //输入命令
            cmds = `mvn io.xc5:xvsa-maven-plugin:1.39:gather -Dxvsa.dir="${this.extensionPath}\\xvsa" -Dxvsa.phantom=true -X -Djfe.opt="-v,-dumpMethodName=true,-win32=true,-libGen=true,-libGenOnly=true" -Dxvsa.lib.gen=true`
        } else {
            cmds = `mvn io.xc5:xvsa-maven-plugin:1.39:gather -Dxvsa.dir=${XVSA} -Dxvsa.phantom=true -X -Djfe.opt="-v,-dumpMethodName=true,-libGenOnly=true,-VTABLE=true" -Dxvsa.lib.gen=true`
        }
        terminalA.sendText(cmds); //输入命令
        clearInterval(this.timer)
        this.fnsList = []
        this.timer = setInterval(() => {
            console.log(this.fnsList.length)
            if (this.fnsList.length) {
                clearInterval(this.timer)
            } else {
                this.getFnList(panel)
            }
        }, 3000);
    }
    //编辑rule数据
    editRule(message: any, panel: any): void {
        let miFileUrl = `${this.fileUrl}/${message.name}.mi`
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
                let miFileUrl = `${this.fileUrl}/${message.name}.mi`
                panel.webview.postMessage({ ruleList: newData, type: 'del', miFileUrl: miFileUrl, name: message.name });
                message.text = newData
                this.saveRule(message, panel)

            }
        })
    }
    //保存rule
    saveRule(message: any, panel: any): void {
        let obj: any = {}
        switch (message.type) {
            case 'del':
                obj = message.text
                let url = `${this.fileUrl}/${message.name}.mi`
                this.deleteFolderRecursive(url)
                fs.writeFile(this.ruleJsonUrl, JSON.stringify(obj, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                break;
            case 'add':
                let fsmJson = message.text
                this.createMi(fsmJson, message) //创建规则mi
                let miFileUrl = `${this.fileUrl}/${message.name}.mi`
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
                    panel.webview.postMessage({ ruleList: obj, type: 'ruleList', miFileUrl: miFileUrl, jarUrl: this.jarUrl, tableMiUrl: this.tableMiUrl });
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
    //生成规则mi
    createMi(fsmJson: JSON, message: any): void {
        let urls = `${this.fileUrl}/${message.name}.mi`
        let jsdata = this.fliter(fsmJson)
        fs.writeFile(urls, jsdata, (err: any) => {
            if (err) { }
        })
    }
    //生的mi文件
    fliter(obj: any) {
        let str = ''
        let DEF_ACTION = ''
        let DECLARE = ''
        let allArr = obj.pens || []
        let nodeList = allArr.filter((item: any) => item.type == 0) || []
        let lines = allArr.filter((item: any) => item.type == 1) || []
        nodeList.forEach((item: any) => {
            str += `NODE|${item.text}\n`
        });
        lines.forEach((item: any) => {
            let txt = item.text
            let arr = txt.includes("|") ? txt.split("|") : []
            let from = allArr.filter((it: any) => item.from.id == it.id)
            let to = allArr.filter((it: any) => item.to.id == it.id)
            if (arr.length) {
                let remarkArr = this.dataListJson.filter((it: any) => it.name == arr[1])
                DECLARE += `DECLARE|${arr[1]}|CUSTOM|${remarkArr.length ? remarkArr[0].remark : ''}\n`
                if (arr.length && arr[0] != "" && arr[0] != '') {
                    str += `EDGE|${from[0]['text']}|${to[0]['text']}|${arr[0]}|none|this()|${arr.length ? arr[1] : 'none'}\n`
                } else {
                    DEF_ACTION += `DEF_ACTION|${from[0]['text']}|${arr[1]}\n`
                }
            } else {
                str += `EDGE|${from[0]['text']}|${to[0]['text']}|${item.text}|none|this()|none\n`
            }
        })
        return `${str}${DEF_ACTION}${DECLARE}`
    }
    //删除delURule
    delURule(message: any, panel: any): void {
        switch (message.type) {
            case "del":
                this.dataListJson = this.dataListJson.filter((item: any) => item.id != message.id)
                fs.writeFile(this.dataListUrl, JSON.stringify(this.dataListJson, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
                panel.webview.postMessage({ type: 'addUrule', status: 'no', dataList: this.dataListJson })
                break;
        }
    }
    //urule 数据
    createDataJson(obj: any, panel: any, type: any): void {
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
            } else if (err && err.code == 'ENOENT') {
                dataArr.push(obj)
                fs.writeFile(this.dataListUrl, JSON.stringify(dataArr, null, "\t"), 'utf-8', (err: any) => {
                    if (err) { err.status(500).send('Server is error...') }
                })
            }
            this.dataListJson = dataArr
            panel.webview.postMessage({ type: 'addUrule', status: 'yes', dataList: dataArr })
        })
    }
    toShell(message: any): void {
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
        let newfile: string = `${this.fileUrl}/${message.name}.mi`
        let fileNames: string = `${newFileUrl}/${message.name}.mi`
        let tableMi: string = `${newFileUrl}/${this.tableMiName}`
        let jarflie: string = `${newFileUrl}/${this.jarName}`
        let configFlie: string = `${newFileUrl}/config.ini`
        let rules: any = []
        this.dataListJson.forEach((item: any) => {
            rules.push({ rulecode: item.name, "ruleset": "CUSTOM", "description": item.remark, "name": item.remark })
        })
        let strConfig: string = `[config]\nname = "${message.name}"\nlang = "java"\nxvsa_path="${XVSA_PATH}"\ninput = "${fileNames}"\nreferences = "${tableMi}"\ndependency = "${jarflie}"\nhost = "${serverIp}"\nuser = "${databaseUser}"\nport = "${databasePort}"\npassword="${databasePassword}"\nrules=${JSON.stringify(rules)}\ntarget = "${tarGetUrl}"`
        let confUrl: string = `${this.fileUrl}/config.ini`
        fs.writeFile(confUrl, strConfig, 'utf-8', (err: any) => {
            if (err) { err.status(500).send('Server is error...') }
        })
        let filLis: any = [this.tableMiUrl, this.jarUrl, newfile, confUrl]
        let fileNameArr: any = [tableMi, jarflie, fileNames, configFlie]
        let pytest: any = ''

        if (!this.sys) {
            pytest = `${this.extensionPath}/test.py`
        } else {
            pytest = `${this.extensionPath}\\test.py`
        }
        terminalB.sendText('cmd'); //输入命令
        terminalB.sendText(`python ${pytest} ${serverUseName} ${serverPasswd} ${serverIp} ${filLis} ${fileNameArr} ${mainpyUrl} ${tarGetUrl} ${newFileUrl}`)
    }
}