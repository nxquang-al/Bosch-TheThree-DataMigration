const express = require("express");

const router = new express.Router();
const path = require("path");

const uploadReqIf = require("../controllers/uploads/uploadReqIf");
const uploadMapping = require("../controllers/uploads/uploadMapping");
const uploadGithub = require("../controllers/uploads/uploadGithub");

router.post(
  "/reqif",
  uploadReqIf.uploadReqIf.single("reqif_file"),
  uploadReqIf.uploadFileReqIF
);

router.post(
  "/mapping",
  uploadMapping.uploadMapping.single("mapping_file"),
  uploadMapping.uploadFileMapping
);

router.post(
  "/github",
  uploadGithub.uploadGithub.single("github_file"),
  uploadGithub.uploadFileGithub
);

module.exports = router;
