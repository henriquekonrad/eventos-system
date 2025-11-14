import express from "express";
import cors from "cors";
import emailRoutes from "./routes/email.js";
import { config } from "./config.js";

const app = express();

app.use(cors());
app.use(express.json());

app.use("/email", emailRoutes);

app.listen(config.port, () => {
  console.log(`Email service iniciado na porta ${config.port}`);
});
