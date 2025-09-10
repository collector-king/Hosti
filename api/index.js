const { InteractionResponseType, verifyKey } = require('discord-interactions');
const express = require('express');
const app = express();

app.use(express.json({
  verify: (req, res, buf, encoding) => {
    const signature = req.get('X-Signature-Ed25519');
    const timestamp = req.get('X-Signature-Timestamp');

    // Check if required headers are present
    if (!signature || !timestamp) {
      res.status(401).send('Missing signature or timestamp');
      throw new Error('Missing signature or timestamp');
    }

    const isValid = verifyKey(buf, signature, timestamp, process.env.PUBLIC_KEY);
    if (!isValid) {
      res.status(401).send('Invalid request signature');
      throw new Error('Invalid signature');
    }
  }
}));

app.post('/interactions', async (req, res) => {
  try {
    const { type, data } = req.body || {};

    if (!type || !data) {
      return res.status(400).send('Invalid interaction data');
    }

    if (type === InteractionResponseType.PING) {
      return res.send({ type: InteractionResponseType.PONG });
    }

    if (type === InteractionResponseType.APPLICATION_COMMAND && data.name === 'ping') {
      return res.send({
        type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data: { content: 'Pong!' },
      });
    }

    res.status(400).send('Unknown interaction');
  } catch (error) {
    console.error('Interaction error:', error);
    res.status(500).send('Internal server error');
  }
});

module.exports = app;
