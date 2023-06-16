const logger = require("./utils/logger");
const app = require("./app");

const port = process.env.PORT || 2023;
const DEFAULT_PORT = 3000;
const HOST = "localhost";

app.listen(port, () => {
  const { 2: mode } = process.argv;
  if (mode) {
    // eslint-disable-next-line
    config[`is${mode[0].toUpperCase()}${mode.slice(1).toLowerCase()}`] = true;
  }
  logger.appStarted(DEFAULT_PORT, HOST, port);
});

module.exports = app; // For testing
