# Decisions

- **Tested my own app, not a demo site.** Findings are real and I can fix them, and it ties to the model card.
- **Added an API.** The Streamlit app has no service interface to test, so I wrapped the model in a small Flask API. Because I wrote it, I did not count API results as defects found; the API tests show contract and validation testing.
- **strict xfail for known defects.** Keeps CI green and the bug documented, and forces cleanup when fixed.
- **Oracle testing.** UI and API outputs are compared with the model called directly.
- **Removed a vacuous test.** A SQL check I first wrote could never fail (`>= 0`), so I deleted it instead of counting it.
- **Test-side bugs fixed along the way:** wrong slider selector, "Male" matching "Female", and a sidebar read before it rendered. None were app defects.
- **Not tested:** performance, security, other browsers, clinical validity.
