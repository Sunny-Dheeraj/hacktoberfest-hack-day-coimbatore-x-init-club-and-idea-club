"""Build comprehensive, curated learning resources for all 24 skills in ProofPath."""

import json
import os

RESOURCES_DATA = [
    # 1. Python
    {
        "id": "py-doc-official",
        "skill": "Python",
        "title": "Official Python 3 Documentation",
        "description": "Comprehensive language reference and tutorial covering core syntax, data structures, and standard library.",
        "type": "documentation",
        "url": "https://docs.python.org/3/tutorial/",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    {
        "id": "py-real-python",
        "skill": "Python",
        "title": "Real Python: Intermediate & Advanced Guides",
        "description": "In-depth guides on decorators, generators, context managers, async/await, and OOP.",
        "type": "guide",
        "url": "https://realpython.com/",
        "difficulty": "intermediate",
        "estimated_time": "4 hours"
    },
    {
        "id": "py-corey-schafer-yt",
        "skill": "Python",
        "title": "Corey Schafer: Python OOP & Best Practices (YouTube)",
        "description": "Complete English-language video lectures covering classes, dunder methods, decorators, and generators.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc",
        "difficulty": "intermediate",
        "estimated_time": "2 hours"
    },
    # 2. JavaScript
    {
        "id": "js-mdn-guide",
        "skill": "JavaScript",
        "title": "MDN Web Docs: JavaScript Guide",
        "description": "The definitive web developer reference on modern ECMAScript, closures, prototypes, and async promises.",
        "type": "documentation",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "difficulty": "beginner",
        "estimated_time": "4 hours"
    },
    {
        "id": "js-info-tutorial",
        "skill": "JavaScript",
        "title": "The Modern JavaScript Tutorial (javascript.info)",
        "description": "Deep architectural dive into the event loop, microtasks, object prototypes, and memory management.",
        "type": "tutorial",
        "url": "https://javascript.info/",
        "difficulty": "intermediate",
        "estimated_time": "6 hours"
    },
    {
        "id": "js-traversy-yt",
        "skill": "JavaScript",
        "title": "Traversy Media: Modern JavaScript Crash Course (YouTube)",
        "description": "Thorough English walkthrough of ES6+, DOM manipulation, fetch API, and async/await.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c",
        "difficulty": "beginner",
        "estimated_time": "1.5 hours"
    },
    # 3. TypeScript
    {
        "id": "ts-handbook-official",
        "skill": "TypeScript",
        "title": "TypeScript Official Handbook",
        "description": "Official handbook covering generics, union/intersection types, conditional types, and utility types.",
        "type": "documentation",
        "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "difficulty": "intermediate",
        "estimated_time": "3 hours"
    },
    {
        "id": "ts-fcc-yt",
        "skill": "TypeScript",
        "title": "freeCodeCamp: TypeScript Full Course for Beginners (YouTube)",
        "description": "Comprehensive English guide on static typing, interfaces, classes, and React with TypeScript.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=BwuLxPH8IDs",
        "difficulty": "beginner",
        "estimated_time": "2 hours"
    },
    # 4. React
    {
        "id": "react-dev-docs",
        "skill": "React",
        "title": "React.dev Official Documentation",
        "description": "Interactive documentation explaining the component model, state batching, hooks, and Suspense.",
        "type": "documentation",
        "url": "https://react.dev/learn",
        "difficulty": "beginner",
        "estimated_time": "4 hours"
    },
    {
        "id": "react-web-dev-simplified-yt",
        "skill": "React",
        "title": "Web Dev Simplified: Learn React Hooks in Detail (YouTube)",
        "description": "Clear English deep dive into useState, useEffect, useMemo, useCallback, and useRef.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLZlA0Gpn_vH8EtggFGERCwMY56Jr9O397",
        "difficulty": "intermediate",
        "estimated_time": "2 hours"
    },
    # 5. Node.js
    {
        "id": "node-doc-official",
        "skill": "Node.js",
        "title": "Node.js Official Documentation & Guides",
        "description": "Reference on event loop phases, Streams, Buffers, Cluster module, and child processes.",
        "type": "documentation",
        "url": "https://nodejs.org/en/docs/guides/",
        "difficulty": "intermediate",
        "estimated_time": "3 hours"
    },
    {
        "id": "node-fcc-yt",
        "skill": "Node.js",
        "title": "freeCodeCamp: Node.js and Express.js Full Course (YouTube)",
        "description": "Step-by-step English tutorial on backend architecture, routing, middleware, and database connections.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=Oe421EPjeBE",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    # 6. FastAPI
    {
        "id": "fastapi-doc-official",
        "skill": "FastAPI",
        "title": "FastAPI Official Interactive Tutorial",
        "description": "Comprehensive tutorial on path operations, Pydantic v2 schemas, Depends injection, and OAuth2.",
        "type": "documentation",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    {
        "id": "fastapi-amigoscode-yt",
        "skill": "FastAPI",
        "title": "Amigoscode: Python FastAPI Tutorial (YouTube)",
        "description": "High-quality English tutorial on building production REST APIs, validation, and Dockerization.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=GN6ICac3OXY",
        "difficulty": "intermediate",
        "estimated_time": "1.5 hours"
    },
    # 7. Flask
    {
        "id": "flask-doc-official",
        "skill": "Flask",
        "title": "Flask Official Documentation",
        "description": "Application factories, Blueprints, request contexts, and WSGI middleware deployment.",
        "type": "documentation",
        "url": "https://flask.palletsprojects.com/en/latest/",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    # 8. Django
    {
        "id": "django-doc-official",
        "skill": "Django",
        "title": "Django Official Documentation & Polls Tutorial",
        "description": "ORM models, migrations, views, Django REST Framework serialization, and authentication.",
        "type": "documentation",
        "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "difficulty": "intermediate",
        "estimated_time": "4 hours"
    },
    # 9. PyTorch
    {
        "id": "pytorch-tutorials",
        "skill": "PyTorch",
        "title": "PyTorch Official Deep Learning Tutorials",
        "description": "Official tutorials covering Tensors, Autograd computational graphs, nn.Module, and custom training loops.",
        "type": "tutorial",
        "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
        "difficulty": "intermediate",
        "estimated_time": "5 hours"
    },
    {
        "id": "pytorch-aladdin-yt",
        "skill": "PyTorch",
        "title": "Aladdin Persson: PyTorch Neural Network Masterclass (YouTube)",
        "description": "Clean English walkthrough of building CNNs, RNNs, custom loss functions, and transfer learning in PyTorch.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLhhyoLH6IjfxeoooqPgh71MW_AzWDpw7f",
        "difficulty": "intermediate",
        "estimated_time": "3 hours"
    },
    # 10. TensorFlow
    {
        "id": "tf-doc-official",
        "skill": "TensorFlow",
        "title": "TensorFlow Core Official Guides",
        "description": "tf.data pipelines, Keras functional API, custom GradientTape training loops, and SavedModel export.",
        "type": "documentation",
        "url": "https://www.tensorflow.org/guide",
        "difficulty": "intermediate",
        "estimated_time": "4 hours"
    },
    # 11. Scikit-learn
    {
        "id": "sklearn-doc-official",
        "skill": "Scikit-learn",
        "title": "Scikit-learn Official User Guide",
        "description": "Supervised & unsupervised algorithms, ColumnTransformer, cross-validation, and hyperparameter tuning.",
        "type": "documentation",
        "url": "https://scikit-learn.org/stable/user_guide.html",
        "difficulty": "intermediate",
        "estimated_time": "4 hours"
    },
    {
        "id": "sklearn-statquest-yt",
        "skill": "Scikit-learn",
        "title": "StatQuest with Josh Starmer: Machine Learning Algorithms (YouTube)",
        "description": "Superb visual English explanations of Random Forests, Gradient Boosting, SVMs, and PCA.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    # 12. Pandas
    {
        "id": "pandas-doc-official",
        "skill": "Pandas",
        "title": "Pandas Official User Guide",
        "description": "10 minutes to pandas, grouping, merging, pivot tables, multi-indexing, and time series handling.",
        "type": "documentation",
        "url": "https://pandas.pydata.org/docs/user_guide/index.html",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    # 13. NumPy
    {
        "id": "numpy-doc-official",
        "skill": "NumPy",
        "title": "NumPy Official Documentation & Tutorials",
        "description": "Vectorization, multidimensional slicing, broadcasting rules, and np.linalg linear algebra operations.",
        "type": "documentation",
        "url": "https://numpy.org/doc/stable/user/index.html",
        "difficulty": "beginner",
        "estimated_time": "2 hours"
    },
    # 14. SQL
    {
        "id": "sql-w3-tutorial",
        "skill": "SQL",
        "title": "SQL Tutorial & Reference",
        "description": "Interactive reference on SELECT, WHERE, JOINs (INNER, LEFT, RIGHT), GROUP BY, and CTE expressions.",
        "type": "tutorial",
        "url": "https://www.w3schools.com/sql/",
        "difficulty": "beginner",
        "estimated_time": "2 hours"
    },
    {
        "id": "sql-mode-analytics",
        "skill": "SQL",
        "title": "Mode Analytics Advanced SQL Tutorial",
        "description": "Window functions (ROW_NUMBER, RANK, LAG/LEAD), subqueries, and performance query tuning.",
        "type": "guide",
        "url": "https://mode.com/sql-tutorial/",
        "difficulty": "advanced",
        "estimated_time": "4 hours"
    },
    {
        "id": "sql-hussein-yt",
        "skill": "SQL",
        "title": "Hussein Nasser: Database Indexing & Query Planning (YouTube)",
        "description": "Outstanding architectural lectures in English on B-Trees, transaction isolation, and ACID locks.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=-qNSXK7s7_w",
        "difficulty": "advanced",
        "estimated_time": "1.5 hours"
    },
    # 15. Git
    {
        "id": "git-pro-book",
        "skill": "Git",
        "title": "Pro Git Book (Official Scott Chacon)",
        "description": "Free official book covering branching, interactive rebasing, merge conflicts, and Git internal object blobs.",
        "type": "documentation",
        "url": "https://git-scm.com/book/en/v2",
        "difficulty": "beginner",
        "estimated_time": "4 hours"
    },
    # 16. Docker
    {
        "id": "docker-get-started",
        "skill": "Docker",
        "title": "Docker Official Documentation: Getting Started",
        "description": "Multi-stage Dockerfiles, image caching, container networking, and docker-compose orchestration.",
        "type": "documentation",
        "url": "https://docs.docker.com/get-started/",
        "difficulty": "beginner",
        "estimated_time": "2 hours"
    },
    {
        "id": "docker-techworld-nana-yt",
        "skill": "Docker",
        "title": "TechWorld with Nana: Docker Tutorial for Beginners (YouTube)",
        "description": "Clear English visual walkthrough of images, containers, ports, volumes, and multi-container Compose.",
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=3c-iBn73dDE",
        "difficulty": "beginner",
        "estimated_time": "2.5 hours"
    },
    # 17. OpenCV
    {
        "id": "opencv-doc-official",
        "skill": "OpenCV",
        "title": "OpenCV-Python Official Tutorials",
        "description": "Image filtering, morphological transforms, Canny edge detection, contours, and video streaming.",
        "type": "documentation",
        "url": "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html",
        "difficulty": "intermediate",
        "estimated_time": "4 hours"
    },
    # 18. Transformers
    {
        "id": "transformers-hf-docs",
        "skill": "Transformers",
        "title": "Hugging Face Transformers Documentation",
        "description": "Pipelines, AutoModel/AutoTokenizer, Trainer API, self-attention mechanisms, and PEFT/LoRA fine-tuning.",
        "type": "documentation",
        "url": "https://huggingface.co/docs/transformers/index",
        "difficulty": "advanced",
        "estimated_time": "5 hours"
    },
    {
        "id": "transformers-jay-alammar",
        "skill": "Transformers",
        "title": "The Illustrated Transformer by Jay Alammar",
        "description": "Acclaimed visual explanation of queries, keys, values, multi-head attention, and encoder-decoder stacks.",
        "type": "guide",
        "url": "https://jalammar.github.io/illustrated-transformer/",
        "difficulty": "intermediate",
        "estimated_time": "1 hour"
    },
    # 19. Machine Learning
    {
        "id": "ml-google-crash-course",
        "skill": "Machine Learning",
        "title": "Google Machine Learning Crash Course",
        "description": "Fast-paced course covering loss curves, regularization, classification thresholds, and feature engineering.",
        "type": "tutorial",
        "url": "https://developers.google.com/machine-learning/crash-course",
        "difficulty": "beginner",
        "estimated_time": "4 hours"
    },
    # 20. Deep Learning
    {
        "id": "dl-mit-course",
        "skill": "Deep Learning",
        "title": "MIT 6.S191: Introduction to Deep Learning",
        "description": "MIT lecture series covering backpropagation, CNNs, Transformers, and generative models.",
        "type": "guide",
        "url": "http://introtodeeplearning.com/",
        "difficulty": "advanced",
        "estimated_time": "5 hours"
    },
    {
        "id": "dl-3blue1brown-yt",
        "skill": "Deep Learning",
        "title": "3Blue1Brown: Neural Networks & Backpropagation (YouTube)",
        "description": "World-class visual English series on gradient descent, multilayer perceptrons, and the calculus of backprop.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",
        "difficulty": "beginner",
        "estimated_time": "1.5 hours"
    },
    # 21. REST API
    {
        "id": "rest-api-design-guide",
        "skill": "REST API",
        "title": "Microsoft RESTful Web API Design Guidelines",
        "description": "Resource URI patterns, idempotency, HTTP status codes, error models, and pagination strategies.",
        "type": "guide",
        "url": "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design",
        "difficulty": "intermediate",
        "estimated_time": "2 hours"
    },
    # 22. Data Analysis
    {
        "id": "data-analysis-kaggle-learn",
        "skill": "Data Analysis",
        "title": "Kaggle Learn: Data Cleaning & Exploratory Analysis",
        "description": "Hands-on exercises on missing value handling, parsing dates, character encodings, and scaling.",
        "type": "practice",
        "url": "https://www.kaggle.com/learn/data-cleaning",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    # 23. Mathematics
    {
        "id": "math-essence-linear-algebra-yt",
        "skill": "Mathematics",
        "title": "3Blue1Brown: Essence of Linear Algebra (YouTube)",
        "description": "The gold-standard English geometric intuition for vectors, matrix transformations, dot products, eigenvalues, and eigenvectors.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    {
        "id": "math-essence-calculus-yt",
        "skill": "Mathematics",
        "title": "3Blue1Brown: Essence of Calculus (YouTube)",
        "description": "Visual English explanations of derivatives, multivariable gradients, chain rule, and optimization.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr",
        "difficulty": "intermediate",
        "estimated_time": "3 hours"
    },
    {
        "id": "math-mml-book",
        "skill": "Mathematics",
        "title": "Mathematics for Machine Learning (Deisenroth, Faisal, Ong)",
        "description": "Comprehensive textbook covering linear algebra, analytic geometry, matrix decompositions, vector calculus, and continuous optimization.",
        "type": "documentation",
        "url": "https://mml-book.github.io/",
        "difficulty": "advanced",
        "estimated_time": "6 hours"
    },
    # 24. Statistics
    {
        "id": "stats-statquest-yt",
        "skill": "Statistics",
        "title": "StatQuest with Josh Starmer: Statistics Fundamentals (YouTube)",
        "description": "Unmatched English pedagogical breakdowns of p-values, hypothesis tests, distributions, variance, and confidence intervals.",
        "type": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9",
        "difficulty": "beginner",
        "estimated_time": "3 hours"
    },
    {
        "id": "stats-openintro",
        "skill": "Statistics",
        "title": "OpenIntro Statistics (Free Text & Labs)",
        "description": "Rigorous foundation in probability distributions, central limit theorem, t-tests, ANOVA, and linear regression.",
        "type": "documentation",
        "url": "https://www.openintro.org/book/os/",
        "difficulty": "intermediate",
        "estimated_time": "5 hours"
    },
]


def main():
    dest_path = os.path.join(os.path.dirname(__file__), "..", "data", "resources.json")
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump({"resources": RESOURCES_DATA}, f, indent=2)
    print(f"Updated data/resources.json with {len(RESOURCES_DATA)} curated resources across all 24 skills!")


if __name__ == "__main__":
    main()
