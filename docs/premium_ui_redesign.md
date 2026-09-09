# Premium White 3D UI Redesign Specification

## 1. Design Philosophy
The AI-DisasterGuard user interface has been elevated to a **Premium White 3D** aesthetic, delivering tactical precision, supreme readability under direct sunlight, and intuitive physical depth.

## 2. Visual Style & Tokens
- **Backgrounds**: Pure White (\`#FFFFFF\`), Off-White (\`#F8FAFC\`), Light Slate Surface (\`#F1F5F9\`).
- **3D Elevation & Depth**:
  * Base Card Shadow: \`0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03)\`
  * Inner Bevel Highlight: \`inset 0 1px 0 rgba(255, 255, 255, 0.9)\`
  * Interactive Hover Elevation: \`transform: translateY(-2px); box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.08)\`
- **Typography & Contrast**: Deep Slate typography (\`#0F172A\`, \`#1E293B\`, \`#475569\`) guaranteeing WCAG AAA compliance.
- **Glassmorphism on White**: Frosted translucent white cards (\`rgba(255, 255, 255, 0.88)\` to \`rgba(255, 255, 255, 0.96)\` with \`backdrop-filter: blur(16px)\`).

## 3. Emergency Accent Preservation
- **Inviolable Color Standard**: RED (\`#EF4444\` / \`#DC2626\`) is preserved for all SOS, beacon, critical alerts, and distress actions. Red is NEVER replaced by blue or cyan for emergency states.
- **Breathing Halo**: Active emergency triggers pulse with an organic breathing halo (\`box-shadow: 0 0 30px rgba(239, 68, 68, 0.5), 0 0 60px rgba(239, 68, 68, 0.25)\`).
- **Semantic Badges**:
  * Critical / Distress: Vivid Red (\`#DC2626\`)
  * Warning / Elevated: Amber (\`#D97706\`)
  * AI Triage / NLP: Royal Purple / Indigo (\`#7C3AED\`)
  * Safe / Resolved: Forest Emerald (\`#059669\`)
