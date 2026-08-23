# whitebox
<a href="https://whitebox-iota.vercel.app/" target="_blank">
  <img width="1400" height="700" alt="hellowhitebox" src="https://github.com/user-attachments/assets/2f9011ad-47ba-414b-adae-61d762d8055e" />
</a>

## problem domain(s):
ai security, ai reliability, cybersecurity, information security, deep learning, explainable ai (XAI)
## problem statement:
deployed machine and deep learning systems increasingly lean on explanation (XAI) tools such as  **SHAP (SHapley Additive exPlanations)** and **LIME (Local Interpretable Model-agnostic Explanations)** to elucidate and justify the model's decision making process and internal workings to auditors and analysts, turning an incomprehensible 'black box' into a more interpretable 'glass box' that provides deeper insights and reasoning concerned with how the ML/DL model arrived at an accurate output.
 
now, the mechanisms behind the working of these industry level tools primarily include perturbing (making deliberate changes) the model's inputs and noticing how the output changes. a threat actor may look for exactly such an entry point - training a model that can detect when it's being probed by these perturbations, and behaving differently in that moment. this can lead to creation of vital blind spots, that may change the narrative of the entire explanation, as the model may actually learn illegitimate patterns in training data and produce corrupt or biased answers while smartly and confidently blaming some other, irrelevant or unrelated feature for the output as a facade - letting incorrect, biased, or outright malicious behavior hide behind an explanation that looks perfectly plausible on the surface to the human factor *relying* on that very algorithm.
 
this raises a huge security question, as such blind spots or extensive trust on these precisely manipulatable tools can affect organisations, infrastructure or millions of users and put them at a risk or susceptible to some kind of loss.
 
## solution:
 
whitebox is a domain-agnostic CLI tool that audits whether a binary-classification model's explanations can be trusted — not just whether it can generate them. it integrates with any model, in any framework, through a single user-supplied adapter file exposing one function: `predict_proba(X)`. that one integration point is deliberately the only framework-specific code in the whole pipeline.
 
once connected, whitebox runs a fixed five-phase audit:
 
1. **explain** — SHAP perturbs the model's inputs and scores each feature's contribution to each prediction. if `shap` isn't installed, whitebox falls back to a permutation-importance approximation instead of crashing, and every report clearly labels which method produced its numbers.
2. **distill** — a shallow, human-readable decision tree is trained to imitate the black box's own predictions (not ground truth), and its agreement rate (fidelity) with the real model is reported honestly.
3. **narrate** *(optional)* — if a groq api key is configured, an LLM converts SHAP numbers into a plain-english sentence per prediction, grounded in the real feature values to prevent fabricated or inverted claims (a small, fast model can still occasionally omit a given fact — this is tracked, not hidden, via a completeness ratio in the report).
4. **attack** — two adversarial audits: an **evasion attack** (nudging top-SHAP features to try to flip a borderline decision) and an **explanation-manipulation attack** (pushing a currently-irrelevant decoy feature to try to hijack the *stated reason* for a decision while the verdict itself stays fixed — the core vulnerability this project investigates).
5. **defend** — three candidate defenses (small-noise smoothing, large-noise smoothing, clipping) are evaluated against the explanation-manipulation attack and compared honestly against the undefended baseline. no defense is assumed to work — if a run shows no improvement, that's reported as-is.
output is written as a narrated terminal report plus `report.txt`, `report.json`, and `surrogate_rules.txt` — a compliance team can read the terminal output, a script can consume the json.

## visit:
take a look at the whitebox website that explains this project! ([click me!](https://whitebox-iota.vercel.app/))
<a href = "https://whitebox-iota.vercel.app/" target="_blank">
 <img width="1400" height="700" alt="expwhitebox" src="https://github.com/user-attachments/assets/9d9daa29-1bad-43df-ba8e-79ec7112eba8" />
</a>


## phase wise flow:
 
| Phase | What happens |
|---|---|
| **1. explain** | SHAP-based feature attribution — which features drive each decision |
| **2. distill** | a shallow, human-readable surrogate decision tree trained to mimic your model, with a measured fidelity score |
| **3. narrate** *(optional)* | a Groq-hosted LLM turns raw attribution numbers into a grounded, plain-English sentence per prediction |
| **4. attack** | two adversarial audits: **evasion** (can the actual decision be flipped?) and **explanation manipulation** (can the *stated reason* be hijacked while the decision stays fixed?) |
| **5. defend** | three candidate defenses (small/large-noise smoothing, clipping) evaluated against the explanation-manipulation attack, with an honest success/failure verdict |
 
every phase runs through **one integration point**: a `predict_proba(X)` function you provide in a small adapter file. whitebox never inspects your model's internals, only ever calls it and reads what comes back, the same blackbox access a real external auditor would have. this is also what makes it framework-agnostic: scikit-learn, XGBoost, TensorFlow, PyTorch, anything.
 
## setting up:
 
```bash
git clone <this-repo>
cd whitebox
pip install -r requirements.txt
pip install -e .
 
# Sanity-check your environment (what's installed, what's missing)
whitebox check-env
 
# Generate a working demo (trains a real model on sklearn's breast
# cancer dataset, no external download, ~5 seconds) so you can see
# the full pipeline run before wiring up your own model
python examples/train_demo_model.py
cd examples/demo
whitebox audit --data demo_data.csv --target target --adapter demo_adapter.py
```
 
that last command runs the entire five-phase pipeline against a real trained model and prints a full descriptive report to your terminal, then saves `report.txt`, `report.json`, and `surrogate_rules.txt` to `whitebox_report/`.
 
### wiring up your own model:
 
1. copy `examples/sklearn_adapter.py` (or `keras_adapter.py` for TensorFlow) to a new file.
2. point it at your saved model and define `predict_proba(X)`.
3. run:
```bash
   whitebox audit --data your_data.csv --target your_label_column --adapter your_adapter.py
```
 
your `--data` CSV must already be numeric and preprocessed the same way your model expects (categorical columns one-hot encoded, numeric columns scaled). whitebox does not preprocess for you, since it has no way to know your model's expected preprocessing.
 
### enabling the LLM narration layer:
 
entirely optional. everything else works with zero API key. to enable it:
 
```bash
export GROQ_API_KEY="your-key-here"     # get a free key at console.groq.com
```
 
or copy `.env.example` to `.env` and paste your key there. See `whitebox/config.py`'s module docstring for full details and why hardcoding a key into source is never the right move.
 
## architecture:
 
```
whitebox/
├── cli.py            # command-line entry point (`whitebox audit`, `whitebox check-env`)
├── config.py          # all tunable settings + where your Groq API key is read from
├── model_adapter.py   # loads and validates your predict_proba(X) adapter file
├── explainers.py       # SHAP wrapper, with a dependency-free fallback mode
├── surrogate.py         # distills your model into a readable decision tree
├── llm_layer.py          # Groq-backed plain-English narration, with grounded prompting
├── attacks.py             # the two adversarial audits — see its module docstring
├── defenses.py              # candidate defenses against the explanation-manipulation attack
├── audit.py                  # orchestrates all five phases into one AuditReport
└── report.py                   # renders the AuditReport as terminal text + saved files
```
 
every module's docstring explains not just *what* it does but *why it's built that way* - start there if you're extending whitebox rather than just running it. `attacks.py` in particular documents a real methodology pitfall (decoy pushes strong enough to accidentally flip the actual decision, contaminating results) that the code explicitly guards against — worth reading before tuning `--decoy-alpha`.
 
 
## tech stack:
 
- **python** — core language, packaged via `pyproject.toml` (pip-installable, editable install)
- **click** — the `whitebox` CLI (`audit`, `check-env` commands)
- **scikit-learn** — the surrogate decision tree, and the demo model
- **shap** *(optional)* — feature attribution; falls back to a labeled permutation-importance approximation if absent
- **groq + python-dotenv** *(optional)* — plain-english LLM narration layer, key loaded via env var, `.env`, or CLI flag
- **pandas / numpy** — data handling
  
## context (read if you want some conceptual briefing, or if you just have time):
 
as sophisticated and cognitive as they get, powering complex models and serving as the brains while making hundreds and thousands of decisions internally to collapse massive input data into one or more simple outputs, deep learning algorithms are infamous for their decades long, black box problem. 
 
a black box - as the name suggests, is a box that exists, but is an opaque and non interpretable entity. one neural network may contain multiple hidden layers ranging from a handful to hundreds, and as that number grows, with it does the model's representational capacity - its ability to capture more complex patterns in the data. this doesn't translate into better performance automatically; deeper networks are also harder to train, more prone to overfitting, and more computationally demanding, so real gains depend heavily on architecture, regularization, and data quality (but that's a story for another day). somewhere along the way, we may reach a point at which our deep learning model performs excellently and meets industry standards but only, that comes at a cost. a tradeoff: as the model becomes more sophisticated, its interpretability vanishes: the model's internal weights become almost impossible to intuitively understand and we (the developers) are clueless about how the model arrived at the very theoretically accurate result it gave us. this is called the popular **“blackbox”** problem associated with deep learning and machine learning algorithms that we frequently come across. 
 
with time, researchers and practitioners in this field tried to use algorithms and frameworks, to comprehend neural networks and pinpoint the factors driving each decision made within it, so that this black box would no longer remain opaque and well, become a ‘glass box’ where all its internal functionings were out in the open for humans to ponder upon. this kind of algorithm or framework that is used to simplify and elucidate another, more convoluted model, was termed **“Explainable AI (XAI)”**, generally organized around goals like *transparency* (can we see how the model works), *interpretability* (can we understand why it made a given decision), and *trust* (can we rely on that explanation being accurate),though the field doesn't converge on one fixed, universally-cited set of pillars, and different frameworks emphasize these differently. Post-hoc explainability became the gold standard for models too complex to interpret directly, with tools like **SHAP (SHapley Additive exPlanations)** and **LIME (Local Interpretable Model-agnostic Explanations)** leading the field.
 
in the broader picture, businesses and organisations today rely on such XAI frameworks by a huge margin for their functionality and revenue. when I thought about it and went down this rabbit hole, i was left wondering, when one algorithm explains another, can we really trust it?
 
this isn't a question about functionality; yes, these currently available tools must have very research backed, robust architecture that should provide accurate explanations and intellectual clarity to devs. the real question is about ***reliability***. 
- how much trust is too much trust?
- how do we know that the model is not secretly learning illegal patterns to provide biased results but pointing to irrelevant features and convincing the reader to look away from the actual problem?
this isn't hypothetical. researchers have already demonstrated that SHAP and LIME are vulnerable to adversarially constructed classifiers: an attacker can build a model that exploits how these tools sample and perturb data, behaving fairly when the explainer is probing it, but discriminating on protected attributes in normal operation, without the explanation ever revealing the deception. what would it take for one, very talented attacker to manipulate the entire XAI pipeline to cover his tracks and maintain persistence to his malice? my undergrad in cybersecurity may have taught me to be more skeptical, because when one tool or service carries the responsibility of reputed organisations having millions of clients, there must be absolutely no room for error. ***zero trust, as they call it, never trust and always verify.***
 
## limitations:

- the permutation-importance fallback (used automatically if `shap` isn't installed) is a rough approximation, not a substitute for real SHAP values — it's clearly labeled in every report it appears in, and should not be used for any report you intend to publish or rely on.
- `--decoy-alpha` and other attack parameters are tuned for standardized (mean-0, std-1) feature spaces. re-tune them if your data isn't scaled that way.
- no defense in `defenses.py` is guaranteed to work on your model. if your results show no defense beating baseline, that's a legitimate finding consistent with adversarial robustness in XAI being an open research problem — not a bug in this tool.
- whitebox audits *explanation trustworthiness*. it does not audit model accuracy, fairness metrics, or data quality — those need their own tooling.
## research papers:
 
1. Fooling LIME and SHAP: Adversarial Attacks on Post hoc Explanation Methods – *Dylan Slack, Sophie Hilgard, Emily Jia, Sameer Singh, and Himabindu Lakkaraju* ([read here](https://arxiv.org/abs/1911.02508))
2. SHLIME: Foiling Adversarial Attacks Fooling SHAP and LIME – *Sam Chauhan, Estelle Duguet, Karthik Ramakrishnan, Hugh Van Deventer, Jack Kruger, and Ranjan Subbaraman* ([read here](https://arxiv.org/abs/2508.11053))
3. Adversarial Robust and Explainable Network Intrusion Detection Systems Based on Deep Learning – *Kudzai Sauka, Gun-Yoo Shin, Dong-Wook Kim, and Myung-Mook Han* ([read here](https://doi.org/10.3390/app12136451))
4. Robust Intrusion Detection System with Explainable Artificial Intelligence – *Betül Güvenç Paltun, Ramin Fuladi, and Rim El Malki* ([read here](https://arxiv.org/abs/2503.05303))
5. Explainable AI-Based Intrusion Detection Systems for Industry 5.0 and Adversarial XAI: A Systematic Review – *Naseem Khan, Kashif Ahmad, Aref Al-Tamimi, Mohammed M. Alani, Amine Bermak, and Issa Khalil* ([read here](https://www.mdpi.com/2078-2489/16/12/1036))

## license:
 
MIT — see `LICENSE`.
 
## contributors and project timeline:
created by: samriddhi guha (samriddhiguha777@gmail.com) 

timeline: july 28 2026 - present

 
