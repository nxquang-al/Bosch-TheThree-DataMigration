import React, { useRef, useState } from "react";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import axios from "axios";
import classnames from "classnames";
import { CircularProgress } from "@mui/material";

const FileUpload = ({ path, fieldName, title }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [fileList, setFileList] = useState(null);
  const [shouldHighlight, setShouldHighlight] = useState(false);
  const [success, setSuccess] = useState(false);
  const inputRef = useRef();

  const preventDefaultHandler = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleUpload = async () => {
    setIsLoading(true);
    const data = new FormData();
    data.append(fieldName, fileList[0]);

    const { status } = await axios.post(
      "http://localhost:2023/uploads" + path,
      data
    );

    setSuccess(status === 200);
    setFileList(null);
    setIsLoading(false);
  };

  const handleChange = (event) => {
    setFileList([event.target.files[0]]);
  };

  return (
    <>
      <input
        type="file"
        ref={inputRef}
        onChange={handleChange}
        style={{ display: "none" }}
      />
      <div
        className={classnames({
          "w-full h-50": true,
          "p-4 grid place-content-center cursor-pointer": true,
          "text-violet-500 rounded-lg": true,
          "border-4 border-dashed ": true,
          "transition-colors": true,
          "border-violet-500 bg-violet-100": shouldHighlight,
          "border-violet-100 bg-violet-50": !shouldHighlight,
        })}
        onDragOver={(e) => {
          preventDefaultHandler(e);
          setShouldHighlight(true);
        }}
        onDragEnter={(e) => {
          preventDefaultHandler(e);
          setShouldHighlight(true);
        }}
        onDragLeave={(e) => {
          preventDefaultHandler(e);
          setShouldHighlight(false);
        }}
        onDrop={(e) => {
          preventDefaultHandler(e);
          const files = Array.from(e.dataTransfer.files);
          setFileList(files);
          setShouldHighlight(false);
        }}
      >
        {!fileList ? (
          <div
            className="flex flex-col items-center"
            onClick={() => {
              inputRef.current?.click();
            }}
          >
            <CloudUploadIcon className="w-10 h-10" />
            <span>
              <span>Choose a {title} File</span> or drag it here
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            {success ? (
              <>
                <p>File uploaded successfully</p>
                <div className="flex gap-2  mt-2">
                  <button className="bg-violet-500 text-violet-50 px-2 py-1 rounded-md">
                    View
                  </button>
                  <button className="border border-violet-500 px-2 py-1 rounded-md">
                    Reload
                  </button>
                </div>
              </>
            ) : (
              <>
                <p>Files to Upload</p>
                {fileList.map((file, i) => {
                  return <span key={i}>{file.name}</span>;
                })}
                <div className="flex gap-2 mt-2">
                  <button
                    className="bg-violet-500 text-violet-50 px-2 py-1 rounded-md"
                    onClick={() => {
                      handleUpload();
                    }}
                  >
                    {isLoading ? (
                      <CircularProgress sx={{ color: "#fff" }} />
                    ) : (
                      "Upload"
                    )}
                  </button>
                  <button
                    className="border border-violet-500 px-2 py-1 rounded-md"
                    onClick={() => {
                      setFileList(null);
                    }}
                  >
                    Clear
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
};

export default FileUpload;
