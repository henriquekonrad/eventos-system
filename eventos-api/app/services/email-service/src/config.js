import dotenv from "dotenv";
dotenv.config();

export const config = {
  port: process.env.PORT || 4005,
  smtp: {
    host: process.env.SMTP_HOST,
    port: process.env.SMTP_PORT,
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
  apiKey: process.env.SERVICE_API_KEY,
};
