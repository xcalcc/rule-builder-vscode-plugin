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

export function convertJson(filePath: String) {
    const fs = require('fs');

    let jsonData = fs.readFileSync(filePath);
    let data = JSON.parse(jsonData);

    let rules = [];
    let maps = [];

    for (var i = 0; i < data.length; i++) {
        rules.push(data[i].rules);
        maps.push(data[i].pathMsg);
    }

    let pathMsg = {offset: 8000, map: maps};

    let output = {rules: rules, pathMsg: pathMsg};

    var convertToJson = JSON.stringify(output, null, "\t");
    fs.writeFileSync('./.rule/rules.json', convertToJson);
}
