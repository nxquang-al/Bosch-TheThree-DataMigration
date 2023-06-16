const express = require("express");
const router = new express.Router();
const path = require("path");
const fs = require("fs");

router.get("/reqif/:filename", (req, res) => {
  const { filename } = req.params;
  const dirname = path.resolve();

  const fullFilePath = path.join(dirname, `reqif_files/${filename}`);
  console.log(fullFilePath);

  try {
    const data = fs.readFileSync(fullFilePath, "utf8");
    res.status(200).send(data);
  } catch (e) {
    console.log(e);
  }
});

router.get("/config/mapping", (req, res) => {
  try {
    const data = fs.readFileSync(
      path.join(path.resolve(), `config/mapping.yml`),
      "utf-8"
    );

    res.status(200).send(data);
  } catch (e) {
    console.log(e);
  }
});

router.get("/config/github", (req, res) => {
  try {
    const data = fs.readFileSync(
      path.join(path.resolve(), `config/github.yml`),
      "utf-8"
    );

    res.status(200).send(data);
  } catch (e) {
    console.log(e);
  }
});

module.exports = router;
