import { makeStyles } from "@mui/styles";
import React, { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import FileView from "./components/FileView";
import { Button } from "@mui/material";

const useStyles = makeStyles(() => ({
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    width: "100vw",
    height: "100vh",
  },
  form: {
    maxWidth: "50vw",
    display: "flex",
    gap: 30,
  },
}));

const App = () => {
  const styles = useStyles();

  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className={styles.container}>
      <div className={styles.form}>
        <FileUpload path="/reqif" fieldName="reqif_file" title="ReqIf" />
        <FileUpload
          path="/mapping"
          fieldName="mapping_file"
          title="Mapping Config"
        />
        <FileUpload
          path="/github"
          fieldName="github_file"
          title="Github Config"
        />
      </div>
      <div>
        <Button onClick={() => setIsLoading((prev) => !prev)}>Click</Button>
        {isLoading ? <FileView filename="config/mapping" /> : ""}
      </div>
    </div>
  );
};

export default App;
