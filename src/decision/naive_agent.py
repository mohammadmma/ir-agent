import time
import random
import logging
logger = logging.getLogger(__name__)

class FastWikipediaAgent:
    def __init__(self, api, target_pages=5000, dev_mode=False):
        self.api = api
        self.collected_titles = set()
        self.dev_mode = dev_mode

        if dev_mode:
            self.target_pages = 50          # 1% of production
            self.budget_phase1 = 30          # proportional seed searches
            self.budget_limit = 150         # hard budget ceiling for dev
            self.min_content = 100 
        else:
            self.target_pages = target_pages
            self.budget_phase1 = 2500
            self.budget_limit = 6400
            self.min_content = 1000
        

        # Expanded to 300+ diverse queries
        self.seed_queries = [
            "Physics", "Chemistry", "Biology", "Mathematics", "Astronomy",
            "Geology", "Computer science", "Artificial intelligence", "Quantum mechanics",
            "Ancient Egypt", "Roman Empire", "World War II", "Renaissance", "Industrial Revolution",
            "Byzantine Empire", "Ancient Greece", "Medieval Europe", "Cold War", "French Revolution",
            "Classical music", "Jazz", "Rock music", "Opera", "Symphony", "Painting", "Sculpture",
            "Literature", "Poetry", "Philosophy", "Ethics", "Buddhism", "Christianity", "Islam",
            "Economics", "Psychology", "Sociology", "Political science", "Anthropology",
            "Football", "Basketball", "Olympic Games", "Tennis", "Cricket", "Baseball",
            "Europe", "Asia", "Africa", "North America", "South America", "Australia", "Antarctica",
            "Mammals", "Birds", "Fish", "Reptiles", "Insects", "Plants", "Trees", "Ecology",
            "Medicine", "Surgery", "Anatomy", "Neuroscience", "Vaccines", "Diseases",
            "English language", "Spanish language", "Chinese language", "French language",
            "United States", "China", "India", "Russia", "Japan", "Germany", "United Kingdom",
            "New York City", "London", "Tokyo", "Paris", "Beijing", "Moscow", "Cairo",
            "Albert Einstein", "Isaac Newton", "Charles Darwin", "Leonardo da Vinci",
            "William Shakespeare", "Ludwig van Beethoven", "Pablo Picasso", "Aristotle",
            "Democracy", "Capitalism", "Socialism", "Communism", "Fascism", "Liberalism",
            "Algebra", "Calculus", "Geometry", "Trigonometry", "Statistics", "Probability",
            "Electricity", "Magnetism", "Optics", "Mechanics", "Thermodynamics",
            "DNA", "Cell biology", "Evolution", "Genetics", "Ecology", "Biochemistry",
            "Stars", "Planets", "Galaxies", "Black holes", "Solar system", "Universe",
            "Mountains", "Rivers", "Oceans", "Forests", "Deserts", "Islands", "Lakes",
            "Novel", "Short story", "Drama", "Epic poetry", "Fiction", "Non-fiction",
            "Theater", "Cinema", "Television", "Radio", "Photography", "Dance",
            "Baroque", "Romanticism", "Impressionism", "Modernism", "Postmodernism",
            "Hinduism", "Judaism", "Taoism", "Confucianism", "Shinto", "Sikhism",
            "Roman law", "Common law", "Civil law", "Constitutional law", "Criminal law",
            "Microeconomics", "Macroeconomics", "International trade", "Finance", "Banking",
            "Cognitive psychology", "Developmental psychology", "Social psychology",
            "Archaeology", "Paleontology", "Anthropology", "Ethnography", "Linguistics",
            "Swimming", "Athletics", "Gymnastics", "Boxing", "Wrestling", "Martial arts",
            "World cuisines", "Italian cuisine", "Chinese cuisine", "French cuisine",
            "Inventions", "Technology", "Engineering", "Architecture", "Design",
            "Renewable energy", "Climate change", "Biodiversity", "Conservation",
            "Internet", "World Wide Web", "Social media", "Mobile technology",
            "Stock market", "Cryptocurrency", "Business", "Marketing", "Entrepreneurship",
            "Human rights", "Civil rights", "Women's rights", "Labor rights",
            "United Nations", "European Union", "NATO", "World Bank", "WHO",
            "Journalism", "Mass media", "Broadcasting", "Publishing", "Newspapers",
            "Education", "University", "School", "Teaching", "Learning",
            "Painting techniques", "Sculpture materials", "Art history", "Art movements",
            "Classical composers", "Modern composers", "Musical instruments", "Music theory",
            "Ancient philosophy", "Medieval philosophy", "Modern philosophy", "Logic",
            "Organic chemistry", "Inorganic chemistry", "Physical chemistry", "Analytical chemistry",
            "Molecular biology", "Cellular biology", "Developmental biology", "Marine biology",
            "Algebra theory", "Number theory", "Graph theory", "Set theory", "Logic mathematics",
            "Particle physics", "Nuclear physics", "Atomic physics", "Condensed matter physics",
            "Planetary science", "Astrophysics", "Cosmology", "Space exploration",
            "Volcanoes", "Earthquakes", "Plate tectonics", "Minerals", "Rocks", "Fossils",
            "Programming", "Software development", "Web development", "Mobile apps",
            "Machine learning", "Deep learning", "Neural networks", "Data science",
            "Ancient Rome", "Ancient China", "Ancient India", "Ancient Persia",
            "Middle Ages", "Age of Discovery", "Enlightenment", "Reformation",
            "World War I", "Vietnam War", "Korean War", "Gulf War", "Iraq War",
            "Impressionist painting", "Abstract art", "Pop art", "Contemporary art",
            "Rock and roll", "Blues", "Country music", "Hip hop", "Electronic music",
            "Epic literature", "Gothic literature", "Romantic literature", "Realist literature",
            "Greek theater", "Roman theater", "Elizabethan theater", "Modern theater",
            "Documentary film", "Animation", "Silent film", "Film noir",
            "Metaphysics", "Epistemology", "Political philosophy", "Philosophy of mind",
            "Catholic Church", "Protestant Reformation", "Eastern Orthodox", "Anglican Church",
            "Islamic architecture", "Buddhist art", "Christian art", "Jewish art",
            "International relations", "Diplomacy", "Foreign policy", "Geopolitics",
            "Clinical psychology", "Abnormal psychology", "Educational psychology",
            "Cultural anthropology", "Physical anthropology", "Linguistic anthropology",
            "World history", "Economic history", "Social history", "Cultural history",
            "Constitutional democracy", "Parliamentary system", "Presidential system",
            "Free market", "Mixed economy", "Planned economy", "Market economy",
            "Cardiovascular system", "Nervous system", "Immune system", "Digestive system",
            "Pharmacology", "Pathology", "Radiology", "Psychiatry", "Pediatrics",
            "Nutrition", "Diet", "Exercise", "Public health", "Epidemiology",
            "Natural selection", "Speciation", "Adaptation", "Biodiversity", "Extinction",
            "Photosynthesis", "Cellular respiration", "Protein synthesis", "Mitosis",
            "Trigonometric functions", "Linear algebra", "Differential equations",
            "Chemical bonding", "Reaction kinetics", "Equilibrium", "Acids and bases",
            "Electromagnetic waves", "Quantum theory", "Relativity", "String theory"
        ]
        self.seed_queries = self.seed_queries[:self.budget_phase1] if dev_mode else self.seed_queries
        logger.info("=" * 20)
        logger.info(f"dev mode = {dev_mode}")
        logger.info("=" * 20)
        logger.info(
            f"Agent initialized with these parameters:\n"
            f"target_pages = {self.target_pages}\n"
            f"budget_phase1 = {self.budget_phase1}\n"
            f"budget_limit = {self.budget_limit}\n"
        )
        

    def collect_dataset(self):
        logger.info("\n" + "="*70)
        logger.info("WIKIPEDIA DATASET COLLECTION")
        logger.info("="*70)
        logger.info(f"Target: {self.target_pages} pages | Budget: 6500 requests\n")

        start_time = time.time()
        candidate_pool = set()

        # PHASE 1: Broad search
        logger.info("PHASE 1: Searching diverse topics...")
        for i, query in enumerate(self.seed_queries):
            if self.api.page_requests_used >= self.budget_phase1:
                break
            if len(candidate_pool) >= 10000:
                break

            try:
                results = self.api.search_pages(query)
                candidate_pool.update(results)
                if (i + 1) % 50 == 0:
                    logger.info(f"  {i+1} searches | {len(candidate_pool)} candidates | {self.api.page_requests_used} requests")
            except Exception:
                continue

        logger.info(f"✓ Phase 1: {len(candidate_pool)} candidates\n")

        # PHASE 2: Fetch pages
        logger.info("PHASE 2: Fetching pages...")
        candidates = list(candidate_pool - self.collected_titles)
        random.shuffle(candidates)

        for page_name in candidates:
            if len(self.collected_titles) >= self.target_pages:
                break
            if self.api.page_requests_used >= self.budget_limit:
                break
            try:
                page_info = self.api.fetch_page(page_name)
                if page_info and len(page_info.get('content', '')) > self.min_content:
                    self.api.save_page(page_info['title'])
                    self.collected_titles.add(page_info['title'])

                    if len(self.collected_titles) % 250 == 0:
                        elapsed = time.time() - start_time
                        rate = len(self.collected_titles) / max(elapsed, 1)
                        eta = (self.target_pages - len(self.collected_titles)) / rate / 60
                        logger.info(f"  {len(self.collected_titles)}/{self.target_pages} | {self.api.page_requests_used} requests | ETA: {eta:.1f}min")
            except Exception:
                continue

        # PHASE 3: Fill if needed
        if len(self.collected_titles) < self.target_pages:
            logger.info(f"\nPHASE 3: Filling remaining...")
            usage = self.api.get_usage_summary()
            extra = list(set(usage['list_of_known_pages']) - self.collected_titles)
            random.shuffle(extra)

            for page_name in extra:
                if len(self.collected_titles) >= self.target_pages:
                    break
                if self.api.page_requests_used >= 6490:
                    break
                try:
                    page_info = self.api.fetch_page(page_name)
                    if page_info and len(page_info.get('content', '')) > self.min_content:
                        self.api.save_page(page_info['title'])
                        self.collected_titles.add(page_info['title'])
                        if len(self.collected_titles) % 100 == 0:
                            logger.info(f"  {len(self.collected_titles)}/{self.target_pages}")
                except Exception:
                    continue


        if len(self.api.dataset) < self.target_pages:
            missing = self.target_pages - len(self.api.dataset)
            logger.info(f"\nFALLBACK: dataset has {len(self.api.dataset)} pages, need +{missing} from already fetched pages...")
            seen_titles = {d['title'] for d in self.api.dataset}
            for p in self.api.fetched_pages:
                if len(self.api.dataset) >= self.target_pages:
                    break
                if p['title'] in seen_titles:
                    continue
                if p['title'] not in self.api.legal_pages:
                    continue
                self.api.dataset.append(p)
                seen_titles.add(p['title'])
            logger.info(f"FALLBACK done: dataset size = {len(self.api.dataset)}")

        elapsed = time.time() - start_time
        logger.info("\n" + "="*70)
        logger.info("COLLECTION COMPLETE!")
        logger.info("="*70)
        logger.info(f"✓ Titles collected: {len(self.collected_titles)}/{self.target_pages}")
        logger.info(f"✓ Pages in dataset: {len(self.api.dataset)}")
        logger.info(f"✓ Requests: {self.api.page_requests_used}/6500")
        logger.info(f"✓ Time: {elapsed/60:.1f} minutes")
        logger.info("="*70 + "\n")
