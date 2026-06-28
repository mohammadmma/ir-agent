"""Seed queries for broad Wikipedia exploration.

This is DATA, not logic. The agent imports these as a list and feeds them to
`repo.search_pages()` during phase 1. Keeping them here (not inside the agent
class) means:
  * The agent stays focused on orchestration logic (SRP).
  * Queries can be swapped/extended without touching the agent.
  * They can be loaded from a file in the future without code changes.
"""

SEED_QUERIES: list[str] = [
    # Sciences
    "Physics", "Chemistry", "Biology", "Mathematics", "Astronomy",
    "Geology", "Computer science", "Artificial intelligence", "Quantum mechanics",
    # History
    "Ancient Egypt", "Roman Empire", "World War II", "Renaissance", "Industrial Revolution",
    "Byzantine Empire", "Ancient Greece", "Medieval Europe", "Cold War", "French Revolution",
    # Arts
    "Classical music", "Jazz", "Rock music", "Opera", "Symphony", "Painting", "Sculpture",
    "Literature", "Poetry", "Philosophy", "Ethics", "Buddhism", "Christianity", "Islam",
    # Social sciences
    "Economics", "Psychology", "Sociology", "Political science", "Anthropology",
    # Sports
    "Football", "Basketball", "Olympic Games", "Tennis", "Cricket", "Baseball",
    # Geography
    "Europe", "Asia", "Africa", "North America", "South America", "Australia", "Antarctica",
    # Nature
    "Mammals", "Birds", "Fish", "Reptiles", "Insects", "Plants", "Trees", "Ecology",
    # Medicine
    "Medicine", "Surgery", "Anatomy", "Neuroscience", "Vaccines", "Diseases",
    # Languages
    "English language", "Spanish language", "Chinese language", "French language",
    # Countries
    "United States", "China", "India", "Russia", "Japan", "Germany", "United Kingdom",
    # Cities
    "New York City", "London", "Tokyo", "Paris", "Beijing", "Moscow", "Cairo",
    # People
    "Albert Einstein", "Isaac Newton", "Charles Darwin", "Leonardo da Vinci",
    "William Shakespeare", "Ludwig van Beethoven", "Pablo Picasso", "Aristotle",
    # Politics
    "Democracy", "Capitalism", "Socialism", "Communism", "Fascism", "Liberalism",
    # Math
    "Algebra", "Calculus", "Geometry", "Trigonometry", "Statistics", "Probability",
    # Physics subfields
    "Electricity", "Magnetism", "Optics", "Mechanics", "Thermodynamics",
    # Biology subfields
    "DNA", "Cell biology", "Evolution", "Genetics", "Ecology", "Biochemistry",
    # Astronomy
    "Stars", "Planets", "Galaxies", "Black holes", "Solar system", "Universe",
    # Geography features
    "Mountains", "Rivers", "Oceans", "Forests", "Deserts", "Islands", "Lakes",
    # Literature forms
    "Novel", "Short story", "Drama", "Epic poetry", "Fiction", "Non-fiction",
    # Performing arts
    "Theater", "Cinema", "Television", "Radio", "Photography", "Dance",
    # Art movements
    "Baroque", "Romanticism", "Impressionism", "Modernism", "Postmodernism",
    # Religions
    "Hinduism", "Judaism", "Taoism", "Confucianism", "Shinto", "Sikhism",
    # Law
    "Roman law", "Common law", "Civil law", "Constitutional law", "Criminal law",
    # Economics subfields
    "Microeconomics", "Macroeconomics", "International trade", "Finance", "Banking",
    # Psychology subfields
    "Cognitive psychology", "Developmental psychology", "Social psychology",
    # Anthropology & linguistics
    "Archaeology", "Paleontology", "Anthropology", "Ethnography", "Linguistics",
    # More sports
    "Swimming", "Athletics", "Gymnastics", "Boxing", "Wrestling", "Martial arts",
    # Food
    "World cuisines", "Italian cuisine", "Chinese cuisine", "French cuisine",
    # Technology
    "Inventions", "Technology", "Engineering", "Architecture", "Design",
    # Environment
    "Renewable energy", "Climate change", "Biodiversity", "Conservation",
    # Digital
    "Internet", "World Wide Web", "Social media", "Mobile technology",
    # Business
    "Stock market", "Cryptocurrency", "Business", "Marketing", "Entrepreneurship",
    # Rights
    "Human rights", "Civil rights", "Women's rights", "Labor rights",
    # Organizations
    "United Nations", "European Union", "NATO", "World Bank", "WHO",
    # Media
    "Journalism", "Mass media", "Broadcasting", "Publishing", "Newspapers",
    # Education
    "Education", "University", "School", "Teaching", "Learning",
    # Art detail
    "Painting techniques", "Sculpture materials", "Art history", "Art movements",
    # Music detail
    "Classical composers", "Modern composers", "Musical instruments", "Music theory",
    # Philosophy detail
    "Ancient philosophy", "Medieval philosophy", "Modern philosophy", "Logic",
    # Chemistry subfields
    "Organic chemistry", "Inorganic chemistry", "Physical chemistry", "Analytical chemistry",
    # Biology subfields
    "Molecular biology", "Cellular biology", "Developmental biology", "Marine biology",
    # Math subfields
    "Algebra theory", "Number theory", "Graph theory", "Set theory", "Logic mathematics",
    # Physics subfields
    "Particle physics", "Nuclear physics", "Atomic physics", "Condensed matter physics",
    # Space
    "Planetary science", "Astrophysics", "Cosmology", "Space exploration",
    # Earth science
    "Volcanoes", "Earthquakes", "Plate tectonics", "Minerals", "Rocks", "Fossils",
    # Computing
    "Programming", "Software development", "Web development", "Mobile apps",
    "Machine learning", "Deep learning", "Neural networks", "Data science",
    # Ancient civilizations
    "Ancient Rome", "Ancient China", "Ancient India", "Ancient Persia",
    # Historical periods
    "Middle Ages", "Age of Discovery", "Enlightenment", "Reformation",
    # Modern wars
    "World War I", "Vietnam War", "Korean War", "Gulf War", "Iraq War",
    # Art movements detail
    "Impressionist painting", "Abstract art", "Pop art", "Contemporary art",
    # Music genres
    "Rock and roll", "Blues", "Country music", "Hip hop", "Electronic music",
    # Literature movements
    "Epic literature", "Gothic literature", "Romantic literature", "Realist literature",
    # Theater history
    "Greek theater", "Roman theater", "Elizabethan theater", "Modern theater",
    # Film
    "Documentary film", "Animation", "Silent film", "Film noir",
    # Philosophy branches
    "Metaphysics", "Epistemology", "Political philosophy", "Philosophy of mind",
    # Christianity detail
    "Catholic Church", "Protestant Reformation", "Eastern Orthodox", "Anglican Church",
    # Religious art
    "Islamic architecture", "Buddhist art", "Christian art", "Jewish art",
    # International relations
    "International relations", "Diplomacy", "Foreign policy", "Geopolitics",
    # Psychology clinical
    "Clinical psychology", "Abnormal psychology", "Educational psychology",
    # Anthropology subfields
    "Cultural anthropology", "Physical anthropology", "Linguistic anthropology",
    # History subfields
    "World history", "Economic history", "Social history", "Cultural history",
    # Government systems
    "Constitutional democracy", "Parliamentary system", "Presidential system",
    # Economic systems
    "Free market", "Mixed economy", "Planned economy", "Market economy",
    # Body systems
    "Cardiovascular system", "Nervous system", "Immune system", "Digestive system",
    # Medical specialties
    "Pharmacology", "Pathology", "Radiology", "Psychiatry", "Pediatrics",
    # Health
    "Nutrition", "Diet", "Exercise", "Public health", "Epidemiology",
    # Evolution
    "Natural selection", "Speciation", "Adaptation", "Biodiversity", "Extinction",
    # Biochemistry
    "Photosynthesis", "Cellular respiration", "Protein synthesis", "Mitosis",
    # Math detail
    "Trigonometric functions", "Linear algebra", "Differential equations",
    # Chemistry detail
    "Chemical bonding", "Reaction kinetics", "Equilibrium", "Acids and bases",
    # Physics frontier
    "Electromagnetic waves", "Quantum theory", "Relativity", "String theory",
]
