const multer = require("multer");

const storage = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, "reqif_file");
  },
  filename(req, file, cb) {
    cb(null, file.originalname);
  },
});

const uploadReqIf = multer({
  storage,
  limits: {
    fileSize: 2000000, // 2MB
  },
});

const uploadFile = async (req, res) => {
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
  uploadFile,
};
