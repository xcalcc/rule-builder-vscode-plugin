const fs = require('fs');

let filePath = './.rule/dataList.json'
let jsonData = fs.readFileSync(filePath);
let data = JSON.parse(jsonData);

let rules = [];
let map = [];

for (var i = 0; i < data.length; i++) {
    rules.push(data[i].rules);
    map.push(data[i].pathMsg);
}

let pathMsg = {};
pathMsg.offset = 8000;
pathMsg.map = map;

let output = {};
output.rules = rules;
output.pathMsg = pathMsg;

var convertToJson = JSON.stringify(output, null, "\t");
fs.writeFileSync('./.rule/rules.json', convertToJson);