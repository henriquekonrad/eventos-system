import express from "express";
import { sendEmail } from "../emailSender.js";
import { config } from "../config.js";

const router = express.Router();

// middleware para validar API key
router.use((req, res, next) => {
  const key = req.headers["x-api-key"];
  if (key !== config.apiKey) {
    return res.status(401).json({ error: "Invalid API KEY" });
  }
  next();
});

router.post("/send", async (req, res) => {
  try {
    const { to, subject, template, data } = req.body;

    if (!to || !subject || !template)
      return res.status(400).json({ error: "Missing parameters" });

    const templates = {
      inscricao: (d) => `
        <h1>Inscrição confirmada</h1>
        <p>Olá ${d.nome}, sua inscrição no evento <b>${d.evento}</b> foi confirmada!</p>
      `,
      cancelamento: (d) => `
        <h1>Inscrição cancelada</h1>
        <p>Sua inscrição no evento <b>${d.evento}</b> foi cancelada.</p>
      `,
      checkin: (d) => `
        <h1>Presença registrada</h1>
        <p>Você registrou presença no evento <b>${d.evento}</b>.</p>
      `,
    };

    const html = templates[template]?.(data);

    if (!html)
      return res.status(400).json({ error: "Template not found" });

    const info = await sendEmail({ to, subject, html });

    return res.json({ success: true, messageId: info.messageId });

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
