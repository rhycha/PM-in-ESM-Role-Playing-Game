# Attribution and third-party material

## Recorded voice

Synthesised locally. Nothing was sent to a hosted service.

| | |
|---|---|
| **Piper** | Neural text-to-speech. MIT licence. https://github.com/rhasspy/piper |
| **LibriTTS-R (en_US, high)** | Multi-speaker voice model, 904 speakers. **CC BY 4.0.** Trained on LibriTTS-R, itself derived from LibriVox public-domain audiobooks. https://huggingface.co/rhasspy/piper-voices |
| **LAME / ffmpeg** | MP3 encoding of the sprite files. LGPL. |

The eighteen speaking parts were cast by measuring the fundamental frequency of 72
LibriTTS speakers and spreading the cast across the range, so that no two characters in
a scene sound alike. Speaker ids and rates are in `tools/make_voices.py`.

Regenerating the audio requires only the model above; see the README.

## The PM² methodology

**PM²** is the project management methodology of the European Commission. The
*PM² Project Management Methodology Guide 3.1* and the *PM²-Agile Guide 3.0.1* are
European Commission publications, freely available from:

https://commission.europa.eu/about/departments-and-executive-agencies/digital-services/pm2-project-management-methodology_en

Neither guide is redistributed here. Page numbers cited throughout point at those
official editions. This project is not affiliated with, endorsed by, or connected to the
European Commission or any PM² certifying body.

## The European Stability Mechanism

The **ESM** is a real intergovernmental institution headquartered in Luxembourg. The
institutional facts used in the case — its governance bodies, its lending toolkit, how it
funds itself — are accurate as background.

**Everything else is invented.** Project CASTOR, Project POLLUX, the Lending Operations
System, Levallois Systems, every budget, date, figure, meeting and person are fiction
written for teaching. No part of this repository describes a real ESM project, a real ESM
system, or a real ESM employee. This project is not affiliated with or endorsed by the ESM.

## The historical figures

Sixteen historical figures appear as characters. Each is a **mnemonic**: the person's
best-known trait is matched to the PM² role whose behaviour it illustrates. They hold
invented modern jobs, say invented things, and none of it reflects the views, character
or history of the real person. They died between 1492 and 2000 and none of them worked in
euro-area crisis finance.

Portraits are generated SVG drawings, not likenesses. `tools/get_portraits.py` can
optionally install genuine public-domain photographs from Wikimedia Commons; it verifies
each file's licence through the Commons API before downloading and writes a credits file.
Three figures are deliberately excluded from that list because photographs of them are
likely still in copyright.

## Built with

Claude (Anthropic) was used throughout as a development and writing partner. All content
was verified against the two official guides; the verification passes are described in
the README.
