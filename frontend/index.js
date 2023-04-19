import React, { useState } from "react";
import ReactDOM from "react-dom";
import { ChakraProvider, Button, Box, Image, VStack } from "@chakra-ui/react";
import { extendTheme } from "@chakra-ui/react";
import axios from "axios";

const theme = extendTheme({
  colors: {
    purple: {
      500: "#805AD5",
    },
  },
});

function App() {
  const [image, setImage] = useState(null);
  const [dalleImage, setDalleImage] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("image", file);

    const response = await axios.post("http://127.0.0.1:5000/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    setImage(URL.createObjectURL(file));
    setDalleImage(response.data.dalleImage);
  };

  return (
    <ChakraProvider theme={theme}>
      <VStack spacing={5} alignItems="center">
        <Box>
          <input type="file" onChange={handleUpload} />
        </Box>
        {image && <Image src={image} alt="Uploaded" />}
        {dalleImage && <Image src={dalleImage} alt="Modernized Painting" />}
      </VStack>
    </ChakraProvider>
  );
}

ReactDOM.render(<App />, document.getElementById("root"));
