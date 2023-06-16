const express = require("express");
const bodyparser = require("body-parser");
// const formidable = require("express-formidable");
const http = require("http");
const app = express();

const cors = require("cors");
const helmet = require("helmet");
const compress = require("compression");
const expressLayouts = require("express-ejs-layouts");

app.use(helmet.crossOriginResourcePolicy({ policy: "cross-origin" }));
app.use(compress());
app.use(expressLayouts);
app.set("view engine", "ejs");

const allowedOrigins = ["http://localhost:3000", "http://localhost:3001"];

app.use(
  cors({
    origin(origin, callback) {
      // allow requests with no origin
      // (like mobile apps or curl requests)
      if (!origin) return callback(null, true);
      if (allowedOrigins.indexOf(origin) === -1) {
        const msg =
          "The CORS policy for this site (" +
          origin +
          ") does not " +
          "allow access from the specified Origin.";
        return callback(new Error(msg), false);
      }
      return callback(null, true);
    },
  })
);

app.use(express.json());

app.use(bodyparser.urlencoded({ extended: false }));

app.use("/uploads", require("./routes/uploads"));
app.use("/file", require("./routes/file"));

module.exports = new http.Server(app);
