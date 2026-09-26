const { exec } = require("child_process");
const fs = require("fs");

function run(userInput) {
  exec("ls " + userInput);
  return eval(userInput);
}

function read(name) {
  return fs.readFileSync(name);
}

module.exports = { run, read };
