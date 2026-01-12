export function serializeDeckContext(deck: any) {
  return `
Deck: ${deck.name}
Format: ${deck.format}
Commander: ${deck.commander}
Cards:
${deck.cards.map((c: any) => `- ${c.name} (${c.set})`).join('\n')}
  `.trim();
}
