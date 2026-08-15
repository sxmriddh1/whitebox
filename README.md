# whitebox

## problem domain(s):
ai security, ai reliability, cybersecurity, information security, deep learning, explainable ai (XAI)

## problem statement:
deployed machine and deep learning systems increasingly lean on explanation (XAI) tools such as  **SHAP (SHapley Additive exPlanations)** and **LIME (Local Interpretable Model-agnostic Explanations)** to elucidate and justify the model's decision making process and internal workings to auditors and analysts, turning an incomprehensible 'black box' into a more interpretable 'glass box' that provides deeper insights and reasoning concerned with how the ML/DL model arrived at an accurate output.

now, the mechanisms behind the working of these industry level tools primarily include perturbing (making deliberate changes) the model's inputs and noticing how the output changes. a threat actor may look for exactly such an entry point - training a model that can detect when it's being probed by these perturbations, and behaving differently in that moment. this can lead to creation of vital blind spots, that may change the narrative of the entire explanation, as the model may actually learn illegitimate patterns in training data and produce corrupt or biased answers while smartly and confidently blaming some other, irrelevant or unrelated feature for the output as a facade - letting incorrect, biased, or outright malicious behavior hide behind an explanation that looks perfectly plausible on the surface to the human factor *relying* on that very algorithm.

this raises a huge security question, as such blind spots or extensive trust on these precisely manipulatable tools can affect organisations, infrastructure or millions of users and put them at a risk or susceptible to some kind of loss.

## solution: 

## installation: 

## utilisation:

## tech stack

## context (read if you want some conceptual briefing, or if you just have time):

as sophisticated and cognitive as they get, powering complex models and serving as the brains while making hundreds and thousands of decisions internally to collapse massive input data into one or more simple outputs, deep learning algorithms are infamous for their decades long, black box problem. 

a black box - as the name suggests, is a box that exists, but is an opaque and non interpretable entity. one neural network may contain multiple hidden layers ranging from a handful to hundreds, and as that number grows, with it does the model's representational capacity - its ability to capture more complex patterns in the data. this doesn't translate into better performance automatically; deeper networks are also harder to train, more prone to overfitting, and more computationally demanding, so real gains depend heavily on architecture, regularization, and data quality (but that's a story for another day). somewhere along the way, we may reach a point at which our deep learning model performs excellently and meets industry standards but only, that comes at a cost. a tradeoff: as the model becomes more sophisticated, its interpretability vanishes: the model's internal weights become almost impossible to intuitively understand and we (the developers) are clueless about how the model arrived at the very theoretically accurate result it gave us. this is called the popular **“blackbox”** problem associated with deep learning and machine learning algorithms that we frequently come across. 

with time, researchers and practitioners in this field tried to use algorithms and frameworks, to comprehend neural networks and pinpoint the factors driving each decision made within it, so that this black box would no longer remain opaque and well, become a ‘glass box’ where all its internal functionings were out in the open for humans to ponder upon. this kind of algorithm or framework that is used to simplify and elucidate another, more convoluted model, was termed **“Explainable AI (XAI)”**, generally organized around goals like *transparency* (can we see how the model works), *interpretability* (can we understand why it made a given decision), and *trust* (can we rely on that explanation being accurate),though the field doesn't converge on one fixed, universally-cited set of pillars, and different frameworks emphasize these differently. Post-hoc explainability became the gold standard for models too complex to interpret directly, with tools like **SHAP (SHapley Additive exPlanations)** and **LIME (Local Interpretable Model-agnostic Explanations)** leading the field.

in the broader picture, businesses and organisations today rely on such XAI frameworks by a huge margin for their functionality and revenue. when I thought about it and went down this rabbit hole, i was left wondering, when one algorithm explains another, can we really trust it?

this isn't a question about functionality; yes, these currently available tools must have very research backed, robust architecture that should provide accurate explanations and intellectual clarity to devs. the real question is about ***reliability***. 
- how much trust is too much trust?
- how do we know that the model is not secretly learning illegal patterns to provide biased results but pointing to irrelevant features and convincing the reader to look away from the actual problem?

this isn't hypothetical. researchers have already demonstrated that SHAP and LIME are vulnerable to adversarially constructed classifiers: an attacker can build a model that exploits how these tools sample and perturb data, behaving fairly when the explainer is probing it, but discriminating on protected attributes in normal operation, without the explanation ever revealing the deception. what would it take for one, very talented attacker to manipulate the entire XAI pipeline to cover his tracks and maintain persistence to his malice? my undergrad in cybersecurity may have taught me to be more skeptical, because when one tool or service carries the responsibility of reputed organisations having millions of clients, there must be absolutely no room for error. ***zero trust, as they call it, never trust and always verify.***

## research papers:

## research papers:

1. Fooling LIME and SHAP: Adversarial Attacks on Post hoc Explanation Methods – *Dylan Slack, Sophie Hilgard, Emily Jia, Sameer Singh, and Himabindu Lakkaraju* ([read here](https://arxiv.org/abs/1911.02508))
2. SHLIME: Foiling Adversarial Attacks Fooling SHAP and LIME – *Sam Chauhan, Estelle Duguet, Karthik Ramakrishnan, Hugh Van Deventer, Jack Kruger, and Ranjan Subbaraman* ([read here](https://arxiv.org/abs/2508.11053))
3. Adversarial Robust and Explainable Network Intrusion Detection Systems Based on Deep Learning – *Kudzai Sauka, Gun-Yoo Shin, Dong-Wook Kim, and Myung-Mook Han* ([read here](https://doi.org/10.3390/app12136451))
4. Robust Intrusion Detection System with Explainable Artificial Intelligence – *Betül Güvenç Paltun, Ramin Fuladi, and Rim El Malki* ([read here](https://arxiv.org/abs/2503.05303))
5. Explainable AI-Based Intrusion Detection Systems for Industry 5.0 and Adversarial XAI: A Systematic Review – *Naseem Khan, Kashif Ahmad, Aref Al-Tamimi, Mohammed M. Alani, Amine Bermak, and Issa Khalil* ([read here](https://www.mdpi.com/2078-2489/16/12/1036))


## contributors and project timeline:
created by: samriddhi guha (samriddhiguha777@gmail.com) 
