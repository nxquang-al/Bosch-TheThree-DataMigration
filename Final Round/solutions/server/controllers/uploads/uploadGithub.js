const multer = require("multer");

const storageGithub = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, "config");
  },
  filename(req, file, cb) {
    cb(null, "github.yml");
  },
});

const uploadGithub = multer({
  storage: storageGithub,
  limits: {
    fileSize: 2000000, // 2MB
  },
});

const uploadFileGithub = async (req, res) => {
  try {
    if (!req.file) {
      throw new Error();
    }

    return res.status(200).send({
      filename: req.file.filename,
    });
  } catch (err) {
    return res.status(500).send({
      message: err.message,
    });
  }
};

module.exports = {
  uploadGithub,
  uploadFileGithub,
};
