const multer = require("multer");

const storageMapping = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, "config");
  },
  filename(req, file, cb) {
    cb(null, "mapping.yml");
  },
});

const uploadMapping = multer({
  storage: storageMapping,
  limits: {
    fileSize: 2000000, // 2MB
  },
});

const uploadFileMapping = async (req, res) => {
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
  uploadMapping,
  uploadFileMapping,
};
