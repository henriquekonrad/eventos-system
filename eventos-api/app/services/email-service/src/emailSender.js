import nodemailer from "nodemailer";
import { config } from "./config.js";

export async function sendEmail({ to, subject, html }) {
  const transporter = nodemailer.createTransport({
    host: config.smtp.host,
    port: config.smtp.port,
    secure: false,
    auth: {
      user: config.smtp.user,
      pass: config.smtp.pass,
    },
  });

  const info = await transporter.sendMail({
    from: `"Sistema de Eventos" <${config.smtp.user}>`,
    to,
    subject,
    html,
  });

  return info;
}

