import React, { useState, useEffect } from "react";
import axios from "axios";
import { makeStyles } from "@mui/styles";

const useStyles = makeStyles(() => ({
  container: {
    border: "1px solid black",
    padding: 5,
  },
}));

const FileView = ({ filename }) => {
  const styles = useStyles();

  const [contentFile, setContentFile] = useState("");

  useEffect(() => {
    const loadContent = async () => {
      const { data } = await axios.get(
        "http://localhost:2023/file/" + filename
      );

      setContentFile(data);
    };

    loadContent();
  }, []);

  return <div className={styles.container}>{contentFile}</div>;
};

export default FileView;
