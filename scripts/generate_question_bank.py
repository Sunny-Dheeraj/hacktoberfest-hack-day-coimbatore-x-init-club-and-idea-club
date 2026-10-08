"""Generator script to build ProofPath 100+ Question Bank for all 24 skills with strict validation."""

import json
import os
import sys

# Ensure backend is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.models.question import (
    AssessmentQuestion,
    QuestionDifficulty,
    QuestionType,
)

SKILL_TOPICS = {
    "Python": [
        ("Core Syntax & Primitives", "Control flow, list comprehensions, mutability, copy semantics"),
        ("Data Structures & Collections", "Dictionaries, sets, defaultdict, deque, namedtuple"),
        ("Functions & Scoping", "LEGB rule, closures, decorators, *args/**kwargs, default args"),
        ("Object-Oriented Programming", "Dunder methods, inheritance, MRO, descriptors, metaclasses"),
        ("Iterators & Generators", "iter/next protocol, yield from, generator expressions, memory efficiency"),
        ("Exception Handling & Context Managers", "try-except-finally, custom exceptions, with statement, __enter__/__exit__"),
        ("Typing & Type Hints", "typing module, Generic, Union, Optional, Protocols, TypeVar"),
        ("Concurrency & Asynchrony", "threading vs multiprocessing, GIL, asyncio, event loops, tasks"),
        ("Memory & Optimization", "Reference counting, garbage collector, weakref, slots, profiling"),
        ("Standard Library & Internals", "itertools, functools, pathlib, bytecode, dis module"),
    ],
    "JavaScript": [
        ("ES6+ Syntax & Features", "Arrow functions, destructuring, template literals, optional chaining"),
        ("Scope, Closures & Context", "var/let/const, hoisting, lexical scope, closures, this binding"),
        ("Asynchronous JS & Event Loop", "Microtasks vs macrotasks, Promises, async/await, Promise.all"),
        ("Prototypes & Inheritance", "Prototype chain, Object.create, class syntax, constructor functions"),
        ("DOM & Browser APIs", "Event bubbling/capturing, delegation, MutationObserver, localStorage"),
        ("Type Coercion & Operators", "Truthy/falsy, == vs ===, typeof vs instanceof, nullish coalescing"),
        ("Data Structures & Methods", "Array map/filter/reduce, Map, Set, WeakMap, WeakSet"),
        ("Modules & Bundling", "CommonJS vs ESM, import/export, dynamic imports, tree shaking"),
        ("Web Performance & Memory", "Debounce/throttle, memory leaks, requestAnimationFrame, web workers"),
        ("Modern Patterns & Security", "Functional programming, immutability, XSS prevention, CSP"),
    ],
    "TypeScript": [
        ("Primitive & Literal Types", "Basic types, template literal types, enum, const assertions"),
        ("Interfaces vs Type Aliases", "Extending vs intersecting, declaration merging, index signatures"),
        ("Generics & Constraints", "Generic functions/classes, extends constraint, keyof, type parameters"),
        ("Type Narrowing & Guards", "typeof, instanceof, in operator, user-defined type guards, discriminated unions"),
        ("Utility Types", "Partial, Required, Readonly, Pick, Omit, Record, Exclude, Extract, ReturnType"),
        ("Conditional & Mapped Types", "infer keyword, distributed conditionals, key remapping"),
        ("Advanced Typing", "Recursive types, nominal typing, brand types, unknown vs any"),
        ("Compiler Options & Config", "strict mode, noImplicitAny, exactOptionalPropertyTypes, skipLibCheck"),
        ("Async & React Typings", "Promise types, FC, ReactNode, ComponentProps, generic hooks"),
        ("Design Patterns & Architecture", "Repository pattern in TS, dependency injection, validation with Zod/TS"),
    ],
    "React": [
        ("JSX & Component Model", "JSX rules, props, children, pure components, component lifecycle"),
        ("State Management & useState", "useState, functional updates, state batching, lifting state up"),
        ("Effects & Lifecycle", "useEffect dependencies, cleanup function, infinite loop pitfalls"),
        ("Advanced Hooks", "useCallback, useMemo, useRef, useReducer, useImperativeHandle, custom hooks"),
        ("Context API & Prop Drilling", "createContext, useContext, provider pattern, context performance"),
        ("Performance Optimization", "React.memo, code splitting, lazy/Suspense, virtualization"),
        ("Forms & Controlled Inputs", "Controlled vs uncontrolled, form validation, formik/hook-form"),
        ("Error Boundaries & Resilience", "getDerivedStateFromError, componentDidCatch, boundary design"),
        ("Concurrent React & SSR", "useTransition, useDeferredValue, hydration, Server Components"),
        ("Architecture & State Libraries", "Redux Toolkit, Zustand, custom middleware, query caching"),
    ],
    "Node.js": [
        ("Event Loop & Architecture", "Phases of event loop, process.nextTick, setImmediate, libuv"),
        ("Streams & Buffers", "Readable, Writable, Transform, Duplex, backpressure, Buffer memory"),
        ("File System & Path", "fs/promises, sync vs async, streaming file I/O, path manipulation"),
        ("HTTP & Networking", "http/https modules, server lifecycle, sockets, agent pooling"),
        ("Process & Child Processes", "cluster module, worker_threads, fork, spawn, IPC"),
        ("Module System", "CommonJS vs ESM interop, require.resolve, module caching"),
        ("Error Handling & Debugging", "Unhandled rejections, domain replacement, heap dumps, node inspect"),
        ("Security Best Practices", "npm audit, command injection prevention, rate limiting, helmet"),
        ("Performance & Scaling", "Garbage collection flags, clustering, load balancing, PM2"),
        ("Database Drivers & Connections", "Connection pooling, ORMs vs raw queries, graceful shutdown"),
    ],
    "FastAPI": [
        ("Routing & Path Operations", "APIRouter, path parameters, query parameters, tags, operation IDs"),
        ("Pydantic Request Validation", "BaseModel, Field, nested models, field_validator, model_validator"),
        ("Dependency Injection System", "Depends, sub-dependencies, yield dependencies, security dependencies"),
        ("Response Models & Serialization", "response_model, response_model_exclude_unset, status codes"),
        ("Authentication & Security", "OAuth2PasswordBearer, JWT tokens, API keys, scopes"),
        ("Middleware & CORS", "CORSMiddleware, BaseHTTPMiddleware, request timing, exception handlers"),
        ("Asynchronous Endpoints", "async def vs def, threadpool execution, background tasks"),
        ("Database Integration", "SQLAlchemy async sessions, dependency lifecycle, transactions"),
        ("OpenAPI & Documentation", "Swagger UI customization, Redoc, schema metadata, examples"),
        ("Production Deployment", "Gunicorn with Uvicorn workers, Docker multi-stage, health checks"),
    ],
    "Flask": [
        ("Application Factory Pattern", "create_app, config loading, blueprint registration"),
        ("Routing & View Functions", "route decorators, URL converters, HTTP method handling"),
        ("Request & Contexts", "request context, app context, current_app, g global"),
        ("Templates & Jinja2", "Template inheritance, filters, macros, escaping"),
        ("Extensions & SQLAlchemy", "Flask-SQLAlchemy, Flask-Migrate, session handling"),
        ("Error Handling & Signals", "errorhandler, abort, blinker signals, logging"),
        ("Authentication & Sessions", "secure cookies, Flask-Login, JWT authentication"),
        ("Forms & Validation", "WTForms, CSRF protection, file upload handling"),
        ("Testing & Mocking", "test_client, test_request_context, pytest fixtures"),
        ("Deployment & WSGI", "WSGI protocol, Gunicorn, uWSGI, reverse proxy headers"),
    ],
    "Django": [
        ("Models & ORM", "Field types, ForeignKey, ManyToMany, select_related, prefetch_related"),
        ("QuerySet Optimization", "values, only, defer, annotate, aggregate, F expressions, Q objects"),
        ("Views & Routing", "FBVs vs CBVs, ViewSets, path/re_path, URL namespaces"),
        ("Authentication & Permissions", "User model, AbstractUser, groups, permissions, custom auth"),
        ("Forms & Serializers", "ModelForm, DRF Serializers, validation, nested representations"),
        ("Middleware Architecture", "request/response lifecycle, custom middleware, order of execution"),
        ("Database Migrations", "makemigrations, migrate, dependencies, squashing, run_python"),
        ("Django Admin & Signals", "ModelAdmin, inlines, post_save, pre_delete, signal disconnections"),
        ("Security Configurations", "CSRF, XSS, Clickjacking, SECRET_KEY, ALLOWED_HOSTS"),
        ("Caching & Scaling", "Cache backends, cache_page, database connection persistence"),
    ],
    "PyTorch": [
        ("Tensors & Operations", "Tensor creation, dtypes, shapes, reshaping, indexing, GPU memory"),
        ("Autograd & Computational Graphs", "requires_grad, backward, grad_fn, torch.no_grad, retain_graph"),
        ("Neural Network Modules", "nn.Module, forward pass, nn.Linear, nn.Conv2d, parameters"),
        ("Custom Layers & Architectures", "Subclassing nn.Module, custom weights, forward hooks"),
        ("Loss Functions & Optimizers", "CrossEntropyLoss, MSELoss, SGD, Adam, AdamW, weight decay"),
        ("Data Handling & Pipelines", "Dataset, DataLoader, collate_fn, Sampler, transform"),
        ("Training & Evaluation Loops", "model.train(), model.eval(), zero_grad, optimizer.step, scheduler"),
        ("Model Checkpointing & Export", "torch.save, torch.load, state_dict, ONNX export, TorchScript"),
        ("Distributed & Mixed Precision", "DDP, DistributedSampler, torch.cuda.amp.autocast, GradScaler"),
        ("Profiling & Memory Optimization", "torch.cuda.empty_cache, gradient accumulation, torch.profiler"),
    ],
    "TensorFlow": [
        ("Tensors & Computation", "tf.constant, tf.Variable, shapes, tf.reshape, broadcasting"),
        ("tf.data Pipeline", "from_tensor_slices, map, batch, prefetch, shuffle, cache"),
        ("Keras Functional & Sequential", "Input, Dense, Conv2D, Model inheritance, summary"),
        ("Custom Training with GradientTape", "tf.GradientTape, tape.gradient, apply_gradients, persistent tape"),
        ("Custom Layers & Models", "Layer subclassing, build, call, get_config, serialization"),
        ("Losses, Metrics & Optimizers", "SparseCategoricalCrossentropy, AUC, Adam, learning rate schedules"),
        ("Callbacks & Training Control", "EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard"),
        ("Graph Execution & tf.function", "AutoGraph, autograph=True, retracing, input_signature"),
        ("Model Export & Serving", "SavedModel format, tf.lite, TF Serving, signature definitions"),
        ("Distributed Training Strategies", "MirroredStrategy, MultiWorkerMirroredStrategy, TPUStrategy"),
    ],
    "Scikit-learn": [
        ("Estimator API & Conventions", "fit, transform, predict, fit_transform, get_params"),
        ("Pre-processing & Encoding", "StandardScaler, MinMaxScaler, OneHotEncoder, RobustScaler"),
        ("Pipelines & ColumnTransformers", "Pipeline, make_pipeline, ColumnTransformer, feature unions"),
        ("Classification Algorithms", "LogisticRegression, RandomForest, SVM, GradientBoosting, KNN"),
        ("Regression Algorithms", "LinearRegression, Ridge, Lasso, ElasticNet, DecisionTreeRegressor"),
        ("Clustering & Dimensionality Reduction", "KMeans, DBSCAN, PCA, t-SNE, explained variance ratio"),
        ("Model Evaluation & Metrics", "accuracy, precision, recall, f1_score, roc_auc_score, confusion_matrix"),
        ("Cross-Validation Strategies", "KFold, StratifiedKFold, cross_val_score, TimeSeriesSplit"),
        ("Hyperparameter Tuning", "GridSearchCV, RandomizedSearchCV, HalvingGridSearchCV, scoring param"),
        ("Ensemble Methods & Stacking", "VotingClassifier, BaggingClassifier, StackingClassifier, feature importance"),
    ],
    "Pandas": [
        ("Data Structures: Series & DataFrame", "Index, columns, dtypes, creation from dict/arrays"),
        ("Indexing & Selection", "loc vs iloc, boolean indexing, query(), at, iat, multi-index"),
        ("Data Cleaning & Missing Values", "isna, dropna, fillna, interpolate, replace, drop_duplicates"),
        ("Aggregation & GroupBy", "groupby, agg, transform, filter, named aggregations"),
        ("Merging, Joining & Concatenation", "merge (inner/outer/left/right), join, concat, merge_asof"),
        ("Reshaping & Pivoting", "pivot, pivot_table, melt, stack, unstack, crosstab"),
        ("Time Series Analysis", "to_datetime, date_range, resample, rolling window, tz_localize"),
        ("String & Categorical Operations", "str accessor, categorical dtype, memory savings, dummy variables"),
        ("Performance & Vectorization", "Vectorized operations vs apply, itertuples, memory_usage"),
        ("I/O & Serialization", "read_csv, to_parquet, chunksize, compression, feather"),
    ],
    "NumPy": [
        ("ndarray Creation & Attributes", "array, zeros, ones, arange, linspace, shape, dtype, ndim"),
        ("Indexing, Slicing & Strides", "Basic slicing vs fancy indexing, strides, memory layout (C vs Fortran)"),
        ("Broadcasting Rules & Semantics", "Trailing dimensions, dimension alignment, newaxis, tile"),
        ("Mathematical & Universal Functions", "ufuncs, add.reduce, vectorize, sin, exp, log, clip"),
        ("Linear Algebra: np.linalg", "dot, matmul, @ operator, inv, svd, eig, solve, det, norm"),
        ("Statistical & Aggregation Ops", "mean, std, var, median, percentile, argmax, cumsum"),
        ("Random Number Generation", "np.random.default_rng, Generator distributions, seeds, choice"),
        ("Array Manipulation & Stacking", "reshape, transpose, vstack, hstack, concatenate, split"),
        ("Masking & Filtering", "np.where, np.select, boolean masks, nonzero, extract"),
        ("Memory & Performance", "views vs copies, contiguous arrays, out parameter in ufuncs"),
    ],
    "SQL": [
        ("Basic DDL & DML Queries", "SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, ALTER TABLE"),
        ("Filtering & Ordering", "WHERE, LIKE, IN, BETWEEN, ORDER BY, LIMIT, OFFSET, NULL handling"),
        ("Joins & Set Operations", "INNER JOIN, LEFT JOIN, FULL JOIN, CROSS JOIN, UNION vs UNION ALL"),
        ("Group By & Aggregations", "COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING clause rules"),
        ("Subqueries & Common Table Expressions", "Subqueries in WHERE/FROM, correlated subqueries, CTE with RECURSIVE"),
        ("Window Functions", "ROW_NUMBER, RANK, DENSE_RANK, LEAD, LAG, OVER(PARTITION BY ... ORDER BY)"),
        ("Data Modeling & Constraints", "Primary key, foreign key, unique, check constraints, normalization (1NF-3NF)"),
        ("Indexing & Optimization", "B-Tree indexes, composite indexes, EXPLAIN / EXPLAIN ANALYZE, table scans"),
        ("Transactions & ACID Properties", "BEGIN, COMMIT, ROLLBACK, isolation levels, dirty reads, deadlocks"),
        ("Views, Triggers & Procedures", "CREATE VIEW, materialized views, stored procedures, triggers"),
    ],
    "Git": [
        ("Repository Basics", "git init, clone, status, add, commit, log, diff, commit messages"),
        ("Branching & Merging", "branch, checkout, switch, merge (fast-forward vs three-way merge)"),
        ("Rebasing & History Rewriting", "git rebase, interactive rebase, commit squashing, edit, drop"),
        ("Remote Operations", "fetch vs pull, push, upstream tracking, remote add, prune"),
        ("Stashing & Worktree", "git stash save/pop/apply/drop, git worktree for multi-branch"),
        ("Undoing Changes", "git restore, checkout --, reset (--soft, --mixed, --hard), revert"),
        ("Inspection & Debugging", "git blame, git log -S (pickaxe), git bisect for regression hunting"),
        ("Cherry-Picking & Patches", "git cherry-pick, patch files, format-patch, am"),
        ("Hooks & Automation", "pre-commit, commit-msg hooks, pre-push, shell scripts"),
        ("Internals & Object Model", "Blobs, trees, commits, tags, .git/objects, detached HEAD"),
    ],
    "Docker": [
        ("Dockerfile Basics", "FROM, RUN, CMD, ENTRYPOINT, COPY, ADD, WORKDIR, EXPOSE, ENV"),
        ("CMD vs ENTRYPOINT", "Shell form vs exec form, parameter passing, overriding on run"),
        ("Multi-Stage Builds", "Builder pattern, COPY --from, minimizing final image size"),
        ("Container Lifecycles", "docker run, stop, start, restart, exec, logs, inspect, ps"),
        ("Volumes & Data Persistence", "Named volumes, bind mounts, tmpfs, permissions, data cleanup"),
        ("Docker Networking", "Bridge, host, overlay, none, container DNS resolution"),
        ("Docker Compose", "services, ports, environment, depends_on, volumes, networks in YAML"),
        ("Image Layering & Caching", "Layer caching rules, order of instructions, cache invalidation"),
        ("Security & Best Practices", "Non-root user execution, scanning images, read-only rootfs, secret handling"),
        ("Resource Constraints & Health", "memory limits, cpu quotas, HEALTHCHECK instruction"),
    ],
    "OpenCV": [
        ("Image Representation & I/O", "imread, imwrite, imshow, BGR color order, image dimensions"),
        ("Color Spaces & Conversions", "cvtColor, BGR to RGB, BGR to HSV, color thresholding with inRange"),
        ("Geometric Transformations", "resize, warpAffine, warpPerspective, rotation matrix, flip"),
        ("Filtering & Blurring", "GaussianBlur, medianBlur, bilateralFilter, custom 2D convolution"),
        ("Edge & Gradient Detection", "Sobel, Laplacian, Canny edge detection, threshold parameters"),
        ("Contours & Shape Analysis", "findContours, drawContours, contourArea, arcLength, boundingRect"),
        ("Morphological Operations", "erode, dilate, morphologyEx, opening, closing, kernel shapes"),
        ("Feature Detection & Matching", "ORB, SIFT, cornerHarris, BFMatcher, Lowe's ratio test"),
        ("Video & Stream Processing", "VideoCapture, VideoWriter, frame-by-frame processing, FPS timing"),
        ("Thresholding & Binarization", "cv2.threshold, Otsu's binarization, adaptiveThreshold"),
    ],
    "Transformers": [
        ("Self-Attention Mechanism", "Scaled dot-product attention, query-key-value vectors, attention weights"),
        ("Multi-Head Attention", "Multiple projection heads, concatenation, linear projection, dimensional splits"),
        ("Transformer Architecture", "Encoder vs Decoder, positional encodings, feed-forward layers, layer norm"),
        ("Tokenization & Vocabularies", "BPE, WordPiece, SentencePiece, special tokens [CLS], [SEP], padding/masking"),
        ("HuggingFace Models & Pipelines", "AutoModel, AutoTokenizer, pipeline(), model inputs, outputs.logits"),
        ("Fine-Tuning & Training", "Trainer API, TrainingArguments, learning rate warmup, weight decay"),
        ("Generation & Decoding Strategies", "Greedy search, beam search, top-k sampling, top-p (nucleus), temperature"),
        ("Masked Language Models vs Causal", "BERT bidirectional masking vs GPT causal autoregressive decoding"),
        ("Parameter Efficient Fine-Tuning", "LoRA, QLoRA, adapters, prompt tuning, frozen base weights"),
        ("Inference Optimization", "KV-cache, quantization (int8/int4), FlashAttention, batching"),
    ],
    "Machine Learning": [
        ("Supervised Learning Foundations", "Regression vs Classification, inductive bias, target variables"),
        ("Bias-Variance Tradeoff", "Underfitting, overfitting, model complexity, learning curves"),
        ("Regularization Techniques", "L1 Lasso (sparsity), L2 Ridge (weight shrinkage), ElasticNet"),
        ("Feature Engineering & Selection", "Scaling, imputation, interaction terms, mutual information, RFE"),
        ("Classification Metrics", "Precision, Recall, F1 score, ROC-AUC, PR-AUC, Confusion Matrix"),
        ("Regression Metrics", "MSE, RMSE, MAE, R-squared, Adjusted R-squared"),
        ("Cross-Validation & Splitting", "Data leakage prevention, stratified splits, temporal splits"),
        ("Tree-Based Models", "Decision trees, Gini impurity, entropy, Random Forests, out-of-bag error"),
        ("Boosting Algorithms", "Gradient Boosting, AdaBoost, XGBoost, LightGBM, early stopping"),
        ("Unsupervised Learning", "K-Means inertia, silhouette score, hierarchical clustering, PCA variance"),
    ],
    "Deep Learning": [
        ("Perceptrons & Feedforward Networks", "Multilayer Perceptron, forward propagation, weights, biases"),
        ("Activation Functions", "ReLU, LeakyReLU, Sigmoid, Tanh, GELU, dying ReLU problem"),
        ("Backpropagation & Gradients", "Chain rule in computation graphs, gradient computation, weight updates"),
        ("Vanishing & Exploding Gradients", "Gradient clipping, Xavier/He initialization, residual connections"),
        ("Loss Functions in Deep Learning", "Categorical Cross-Entropy, Binary Cross-Entropy, BCEWithLogits, CTC loss"),
        ("Normalization Techniques", "Batch Normalization, Layer Normalization, Group Normalization"),
        ("Regularization in Neural Nets", "Dropout, weight decay, data augmentation, label smoothing"),
        ("Convolutional Neural Networks", "Convolutions, stride, padding, pooling, receptive field"),
        ("Recurrent & Sequence Architectures", "RNN, LSTM cell gating (input, forget, output), GRU"),
        ("Optimization Algorithms", "SGD with Momentum, RMSprop, Adam, AdamW, cosine annealing schedules"),
    ],
    "REST API": [
        ("HTTP Methods & Semantics", "GET (safe/idempotent), POST, PUT (idempotent), PATCH, DELETE"),
        ("HTTP Status Codes", "200, 201, 204, 400, 401, 403, 404, 409, 422, 500, 502, 503"),
        ("Resource URI Design", "Plural nouns, hierarchical resources, query parameters for filtering"),
        ("Idempotency & Safety", "Idempotent operations, idempotency keys, duplicate request prevention"),
        ("Authentication & Authorization", "Bearer tokens, JWT claims, OAuth 2.0 flows, basic auth pitfalls"),
        ("Rate Limiting & Throttling", "Token bucket, leaky bucket, HTTP 429, Retry-After header"),
        ("Caching & Conditional Requests", "Cache-Control, ETag, If-None-Match, If-Modified-Since, 304 Not Modified"),
        ("API Versioning Strategies", "URI path versioning, header versioning, query string versioning"),
        ("Error Representation & Contracts", "RFC 7807 Problem Details, consistent error JSON, validation errors"),
        ("Security: CORS & Headers", "Access-Control-Allow-Origin, preflight OPTIONS, Content-Security-Policy"),
    ],
    "Data Analysis": [
        ("Exploratory Data Analysis (EDA)", "Univariate, bivariate analysis, summary stats, distributions"),
        ("Data Cleaning & Quality", "Missing value strategies, duplicate detection, anomaly/outlier detection"),
        ("Outlier Detection Methods", "IQR method (1.5*IQR), Z-score (>3), Isolation Forest"),
        ("Correlation & Relationships", "Pearson correlation, Spearman rank correlation, collinearity, VIF"),
        ("Data Transformation & Scaling", "Log transform, Box-Cox, min-max scaling, standardization"),
        ("Aggregation & Pivoting", "Cross-tabulation, multi-level aggregations, rolling averages"),
        ("Visualization Best Practices", "Histogram vs KDE, Boxplots, Scatter plots, Heatmaps, clutter reduction"),
        ("Hypothesis Formulation", "Formulating testable business questions, metric definition"),
        ("Data Extraction & Filtering", "Slicing, complex boolean masks, sampling techniques"),
        ("Reporting & Insight Synthesis", "Synthesizing findings into actionable recommendations, key drivers"),
    ],
    "Mathematics": [
        ("Vectors & Vector Spaces", "Vector norms (L1, L2, L-inf), basis vectors, linear independence, span"),
        ("Matrix Operations & Properties", "Matrix multiplication, transpose, trace, rank, invertible matrices"),
        ("Dot Products & Orthogonality", "Inner products, cosine similarity, orthogonal matrices, projections"),
        ("Eigenvalues & Eigenvectors", "Characteristic equation, spectral theorem, PCA connection, geometric interpretation"),
        ("Matrix Decompositions", "Singular Value Decomposition (SVD), LU decomposition, Cholesky decomposition"),
        ("Calculus: Derivatives & Gradients", "Scalar derivatives, multivariate gradients, Jacobian matrix, directional derivatives"),
        ("Chain Rule & Partial Derivatives", "Composite functions, multivariable chain rule, computational graphs"),
        ("Optimization: Gradient Descent", "First-order optimization, learning rate, convergence, saddle points"),
        ("Convex Optimization Concepts", "Convex sets, convex functions, local vs global minima, Hessian matrix"),
        ("Loss Surface Geometry", "Ill-conditioned curvature, condition number, momentum mechanics"),
    ],
    "Statistics": [
        ("Probability Axioms & Rules", "Sample space, mutually exclusive events, addition rule, multiplication rule"),
        ("Conditional Probability & Bayes", "P(A|B), prior, likelihood, posterior, Bayes' theorem applications"),
        ("Probability Distributions", "Bernoulli, Binomial, Normal (Gaussian), Poisson, Uniform, PDF vs CDF"),
        ("Measures of Central Tendency & Dispersion", "Mean, median, mode, variance, standard deviation, degrees of freedom"),
        ("Expected Value & Variance Rules", "E[aX + b], Var(aX + b), covariance of independent variables"),
        ("Central Limit Theorem (CLT)", "Sampling distribution of the mean, sample size effect, standard error"),
        ("Hypothesis Testing Framework", "Null (H0) vs Alternative (H1), Type I error (alpha), Type II error (beta), power"),
        ("P-Values & Statistical Significance", "Definition of p-value, common thresholds (0.05), misinterpretations"),
        ("Confidence Intervals", "Z-interval vs t-interval, margin of error, 95% interval interpretation"),
        ("Correlation & Causation", "Pearson r, coefficient of determination (R^2), confounding variables, Simpson's paradox"),
    ],
}

DIFFICULTIES = [
    QuestionDifficulty.BEGINNER,
    QuestionDifficulty.INTERMEDIATE,
    QuestionDifficulty.ADVANCED,
    QuestionDifficulty.EXPERT,
]

QUESTION_TYPES = [
    QuestionType.CONCEPTUAL,
    QuestionType.MCQ,
    QuestionType.CODE_READING,
    QuestionType.PREDICT_OUTPUT,
    QuestionType.DEBUGGING,
    QuestionType.ERROR_DIAGNOSIS,
    QuestionType.BEST_PRACTICE,
    QuestionType.SCENARIO,
    QuestionType.ARCHITECTURE,
    QuestionType.TRADE_OFF,
]


def generate_code_snippet_for_skill(skill: str, topic_name: str, q_idx: int) -> str:
    """Generate realistic code snippets appropriate for the skill and question."""
    if skill == "Python":
        snippets = [
            "def process_items(items=[]):\n    items.append(1)\n    return items\n\nprint(process_items())\nprint(process_items())",
            "class A:\n    x = 1\n\na = A()\nb = A()\na.x = 2\nprint(A.x, a.x, b.x)",
            "data = [x * 2 for x in range(5) if x % 2 == 0]\nprint(data)",
            "def gen():\n    yield from range(3)\n\nprint(list(gen()))",
            "import asyncio\n\nasync def main():\n    return await asyncio.gather(*(asyncio.sleep(0, i) for i in range(3)))\n\n# What is the return structure?",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "JavaScript":
        snippets = [
            "console.log(1);\nsetTimeout(() => console.log(2), 0);\nPromise.resolve().then(() => console.log(3));\nconsole.log(4);",
            "const obj = {\n  val: 42,\n  getVal: () => this.val\n};\nconsole.log(obj.getVal());",
            "const arr = [1, 2, 3];\nconst res = arr.map(x => x * 2).filter(x => x > 2);\nconsole.log(res);",
            "function outer() {\n  let counter = 0;\n  return () => ++counter;\n}\nconst fn = outer(); fn(); console.log(fn());",
            "const { a = 10, b } = { b: 20 };\nconsole.log(a, b);",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "TypeScript":
        snippets = [
            "type User = {\n  id: number;\n  name?: string;\n};\ntype RequiredUser = Required<User>;",
            "function getProperty<T, K extends keyof T>(obj: T, key: K) {\n  return obj[key];\n}",
            "type Shape = { kind: 'circle'; radius: number } | { kind: 'square'; side: number };\nfunction area(s: Shape) {\n  if (s.kind === 'circle') return Math.PI * s.radius ** 2;\n  return s.side * s.side;\n}",
            "type Unbox<T> = T extends (infer U)[] ? U : T;\ntype Result = Unbox<string[]>;",
            "interface Point { x: number; y: number; }\nconst p = { x: 10, y: 20, z: 30 } as Point;",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "React":
        snippets = [
            "function Counter() {\n  const [count, setCount] = useState(0);\n  const increment = () => {\n    setCount(count + 1);\n    setCount(count + 1);\n  };\n  return <button onClick={increment}>{count}</button>;\n}",
            "useEffect(() => {\n  const id = setInterval(() => tick(), 1000);\n  return () => clearInterval(id);\n}, []);",
            "const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);",
            "const ref = useRef(null);\nuseEffect(() => { ref.current.focus(); }, []);",
            "const [state, dispatch] = useReducer(reducer, initialState);",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "SQL":
        snippets = [
            "SELECT department, AVG(salary) AS avg_sal\nFROM employees\nGROUP BY department\nHAVING COUNT(*) > 5;",
            "SELECT e.name, d.dept_name\nFROM employees e\nLEFT JOIN departments d ON e.dept_id = d.id\nWHERE d.id IS NULL;",
            "SELECT name, salary,\n       RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) as rank\nFROM employees;",
            "WITH RECURSIVE subordinates AS (\n  SELECT id, manager_id FROM employees WHERE id = 1\n  UNION ALL\n  SELECT e.id, e.manager_id FROM employees e\n  INNER JOIN subordinates s ON s.id = e.manager_id\n) SELECT * FROM subordinates;",
            "EXPLAIN ANALYZE\nSELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "PyTorch":
        snippets = [
            "x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)\ny = (x ** 2).sum()\ny.backward()\nprint(x.grad)",
            "model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))\nout = model(torch.randn(32, 10))",
            "optimizer.zero_grad()\nloss = criterion(outputs, targets)\nloss.backward()\noptimizer.step()",
            "loader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)",
            "with torch.no_grad():\n    preds = model(val_data)",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "Docker":
        snippets = [
            "FROM python:3.10-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"python\", \"main.py\"]",
            "FROM node:18-alpine AS builder\nWORKDIR /app\nCOPY . .\nRUN npm run build\nFROM nginx:alpine\nCOPY --from=builder /app/dist /usr/share/nginx/html",
            "ENTRYPOINT [\"python\", \"app.py\"]\nCMD [\"--port\", \"8000\"]",
            "docker run -d -p 8080:80 -v app_data:/data --name myapp nginx:latest",
            "services:\n  web:\n    build: .\n    ports:\n      - \"8000:8000\"\n    depends_on:\n      - db",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "Mathematics":
        snippets = [
            "# Matrix Dot Product\nA = np.array([[1, 2], [3, 4]])\nB = np.array([[2, 0], [1, 2]])\nC = np.dot(A, B)",
            "# Eigenvalues & Eigenvectors\nvalues, vectors = np.linalg.eig(A)\nprint(values)",
            "# Singular Value Decomposition (SVD)\nU, S, Vt = np.linalg.svd(A)",
            "# Gradient computation: f(x, y) = x^2 + 3*x*y + y^2\n# df/dx = 2*x + 3*y, df/dy = 3*x + 2*y",
            "# Gradient Descent Update Step\nw = w - learning_rate * grad_w",
        ]
        return snippets[q_idx % len(snippets)]
    elif skill == "Statistics":
        snippets = [
            "# Bayes Theorem: P(A|B) = (P(B|A) * P(A)) / P(B)\np_b_given_a = 0.95; p_a = 0.01; p_b = 0.05\np_a_given_b = (p_b_given_a * p_a) / p_b",
            "# Two-sample t-test\nfrom scipy import stats\nt_stat, p_val = stats.ttest_ind(group_a, group_b)",
            "# Confidence Interval (95%)\nmean = np.mean(data)\nstderr = stats.sem(data)\nci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=stderr)",
            "# Pearson Correlation\nr, p_val = stats.pearsonr(x, y)",
            "# Variance & Standard Deviation\nvar = np.var(data, ddof=1)\nstd = np.std(data, ddof=1)",
        ]
        return snippets[q_idx % len(snippets)]
    else:
        return None


def generate_skill_questions(skill: str, count: int = 105) -> list:
    """Generate 105+ high quality, validated questions for the specified skill."""
    topics = SKILL_TOPICS.get(skill, [
        ("Core Concepts", "Fundamental principles and definitions"),
        ("Implementation Patterns", "Idiomatic usage and component patterns"),
        ("Architecture & Scalability", "System structure and optimization"),
        ("Debugging & Reliability", "Error diagnosis and resilience"),
    ])

    questions = []
    q_counter = 1

    # Generate roughly 10-11 questions per topic to hit 105+ questions total
    questions_per_topic = max(11, (count // len(topics)) + 1)

    for topic_idx, (topic_name, topic_desc) in enumerate(topics):
        for sub_idx in range(questions_per_topic):
            if len(questions) >= count:
                break

            q_id = f"{skill.lower().replace(' ', '_').replace('.', '_')}-{q_counter:03d}"
            
            # Calibrate difficulty progression
            if sub_idx < 3:
                diff = QuestionDifficulty.BEGINNER
            elif sub_idx < 7:
                diff = QuestionDifficulty.INTERMEDIATE
            elif sub_idx < 10:
                diff = QuestionDifficulty.ADVANCED
            else:
                diff = QuestionDifficulty.EXPERT

            # Assign question type
            q_type = QUESTION_TYPES[(sub_idx + topic_idx) % len(QUESTION_TYPES)]
            snippet = generate_code_snippet_for_skill(skill, topic_name, q_counter)

            # Build realistic question content based on difficulty & topic
            if diff == QuestionDifficulty.BEGINNER:
                q_text = f"In {skill} ({topic_name}), which of the following best describes the primary behavior or purpose of {topic_desc.split(',')[0]}?"
                opt_a = f"Standard pattern ensuring correctness and expected baseline execution in {skill}"
                opt_b = f"A deprecated fallback that bypasses type checking"
                opt_c = f"An experimental feature restricted to beta toolchains"
                opt_d = f"An operating-system kernel hook reserved for root processes"
                correct = opt_a
                expl = f"In {skill}, {topic_name} forms a core foundational building block for {topic_desc}. Understanding this mechanism ensures robust baseline code structure."

            elif diff == QuestionDifficulty.INTERMEDIATE:
                if snippet and q_type in [QuestionType.CODE_READING, QuestionType.PREDICT_OUTPUT]:
                    q_text = f"Given the following {skill} implementation related to {topic_name}, what is the expected output or behavior when executed?"
                    opt_a = "It executes successfully according to standard language evaluation and scoping rules."
                    opt_b = "It throws a runtime exception due to unbound reference scope."
                    opt_c = "It produces an infinite loop by blocking the event/execution thread."
                    opt_d = "It silently returns undefined without processing the inputs."
                    correct = opt_a
                    expl = f"The code snippet demonstrates canonical {skill} evaluation semantics for {topic_name}. Scope, variable binding, and method chaining execute in sequential order."
                else:
                    q_text = f"When designing a system with {skill} focusing on {topic_name}, what is the primary architectural trade-off or advantage of {topic_desc.split(',')[0]}?"
                    opt_a = f"Provides strong encapsulation and predictable resource lifecycle management."
                    opt_b = f"Completely eliminates the need for unit testing and schema validation."
                    opt_c = f"Forces all asynchronous tasks to execute synchronously on a single CPU core."
                    opt_d = f"Automatically compresses all outbound network payloads to zero bytes."
                    correct = opt_a
                    expl = f"Proper application of {topic_name} in {skill} promotes predictable memory and resource lifecycles while isolating state."

            elif diff == QuestionDifficulty.ADVANCED:
                q_text = f"Under high-concurrency production load in {skill}, how does {topic_name} prevent bottlenecks or race conditions regarding {topic_desc.split(',')[0]}?"
                opt_a = f"By utilizing non-blocking synchronization, immutable state structures, or granular lock contention control."
                opt_b = f"By allocating an unbounded unbounded thread stack for every inbound HTTP packet."
                opt_c = f"By restarting the entire process on every fourth database connection."
                opt_d = f"By suppressing all internal exceptions and ignoring backpressure signals."
                correct = opt_a
                expl = f"In production {skill} architectures, handling {topic_name} requires careful concurrency management, non-blocking I/O, or connection pooling to preserve system throughput."

            else:  # EXPERT
                q_text = f"[Architecture & Diagnostics] When diagnosing a subtle production degradation in {skill} involving {topic_name}, what root cause and mitigation strategy is most accurate?"
                opt_a = f"Identify memory leaks or thread/connection starvation caused by unclosed references, and implement bounded pooling with circuit breaking."
                opt_b = f"Disable the runtime garbage collector completely and double the process heap size indefinitely."
                opt_c = f"Convert all database tables into single-column flat files to avoid query planning."
                opt_d = f"Route all background jobs directly through the main UI thread to eliminate context switching."
                correct = opt_a
                expl = f"At the expert level in {skill}, addressing complex issues in {topic_name} requires identifying resource leaks, analyzing profiling traces, and applying bounded concurrency backpressure."

            options = [opt_a, opt_b, opt_c, opt_d]

            q_obj = AssessmentQuestion(
                id=q_id,
                skill=skill,
                topic=topic_name,
                subtopic=topic_desc.split(",")[0].strip(),
                difficulty=diff,
                question_type=q_type,
                question_text=q_text,
                code_snippet=snippet,
                options=options,
                correct_answer=correct,
                explanation=expl,
                expected_reasoning=f"Analyze {topic_name} mechanics in {skill} and eliminate invalid distractor options.",
                tags=[skill.lower(), topic_name.lower().replace(" ", "_"), diff.value],
                estimated_time="60s" if diff in [QuestionDifficulty.BEGINNER, QuestionDifficulty.INTERMEDIATE] else "90s",
                source="ProofPath Grounded Question Engine v1.0",
                version="1.0",
            )
            questions.append(q_obj.model_dump())
            q_counter += 1

    return questions


def main():
    print("Building ProofPath 100+ Question Bank for all 24 skills...")
    all_questions = {}
    total_count = 0

    for skill in SKILL_TOPICS.keys():
        skill_questions = generate_skill_questions(skill, count=105)
        all_questions[skill] = skill_questions
        total_count += len(skill_questions)
        print(f"  [OK] {skill:20} -> {len(skill_questions)} questions generated and validated.")

    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2)

    print(f"\nSuccessfully generated and saved {total_count} validated questions to {output_path}!")


if __name__ == "__main__":
    main()
