const multer = require("multer");

const storageReqIf = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, "reqif_files");
  },
  filename(req, file, cb) {
    cb(null, file.originalname);
  },
});

const uploadReqIf = multer({
  storage: storageReqIf,
  limits: {
    fileSize: 2000000, // 2MB
  },
});

const uploadFileReqIF = async (req, res) => {
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
  uploadReqIf,
  uploadFileReqIF,
};
