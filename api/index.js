const { InteractionResponseType, verifyKey } = require('discord-interactions');
const express = require('express');
const app = express();

app.use(express.json({ verify: (req, res, buf) => {
  const signature = req.get('X-Signature-Ed25519');
  const timestamp = req.get('X-Signature-Timestamp');
  const isValid = verifyKey(buf, signature, timestamp, process.env.PUBLIC_KEY);
  if (!isValid) {
    res.status(401).send('Bad request signature');
    throw new Error('Invalid signature');
  }
}}));

app.post('/interactions', async (req, res) => {
  const { type, data } = req.body;
  if (type === 1) { // PING
    return res.send({ type: InteractionResponseType.PONG });
  }
  if (type === 2 && data.name === 'ping') { // Application Command
    return res.send({
      type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
      data: { content: 'Pong!' },
    });
  }
  res.status(400).send('Unknown interaction');
});

module.exports = app;
