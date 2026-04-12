# Witness Build Modifications — From Jared 2026-02-24

## Modification 1: OAuth Button Text
CHANGE: "Authorize Your AiCIV →"
TO: "Authorize [aiName]'s AI Brain →"
(use payTestData.aiName dynamically)

## Modification 2: Portal Button — Text + Style
CHANGE: "Enter Your AiCIV"
TO: "Enter [aiName]'s Brain Stream"

STYLE: Must match the "Begin Awakening" button on the pre-payment chatbox:
- Large, prominent, eye-catching
- Orange + blue gradient (like the awakening button)
- Same weight/impact — this is the CTA of the entire flow
- Example CSS reference: look at the existing .pb-begin-awakening or similar class in the chatbox plugin
- This button should feel like a MOMENT — the customer is about to enter their AI's world

Dynamic text: "Enter ${payTestData.aiName}'s Brain Stream"
