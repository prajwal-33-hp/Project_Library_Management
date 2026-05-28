from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import hashlib
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'libravault2024')

_db_initialised = False

# ── Database Configuration ──────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST',     'localhost'),
    'port': int(os.environ.get('MYSQL_PORT',     3306)),
    'user':     os.environ.get('MYSQL_USER',     'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'library_db')
}

# 500 Books Data
BOOKS_DATA = [
    # Classic Literature (50 books)
    ("The Great Gatsby", "F. Scott Fitzgerald", 5),
    ("To Kill a Mockingbird", "Harper Lee", 4),
    ("1984", "George Orwell", 7),
    ("Pride and Prejudice", "Jane Austen", 6),
    ("The Catcher in the Rye", "J.D. Salinger", 3),
    ("Brave New World", "Aldous Huxley", 5),
    ("The Grapes of Wrath", "John Steinbeck", 4),
    ("Of Mice and Men", "John Steinbeck", 6),
    ("Lord of the Flies", "William Golding", 5),
    ("Animal Farm", "George Orwell", 8),
    ("Wuthering Heights", "Emily Brontë", 4),
    ("Jane Eyre", "Charlotte Brontë", 5),
    ("Great Expectations", "Charles Dickens", 6),
    ("Oliver Twist", "Charles Dickens", 4),
    ("A Tale of Two Cities", "Charles Dickens", 5),
    ("David Copperfield", "Charles Dickens", 3),
    ("Moby Dick", "Herman Melville", 4),
    ("The Scarlet Letter", "Nathaniel Hawthorne", 5),
    ("Don Quixote", "Miguel de Cervantes", 3),
    ("Anna Karenina", "Leo Tolstoy", 4),
    ("War and Peace", "Leo Tolstoy", 3),
    ("Crime and Punishment", "Fyodor Dostoevsky", 5),
    ("The Brothers Karamazov", "Fyodor Dostoevsky", 4),
    ("The Idiot", "Fyodor Dostoevsky", 3),
    ("Madame Bovary", "Gustave Flaubert", 4),
    ("Les Misérables", "Victor Hugo", 5),
    ("The Hunchback of Notre-Dame", "Victor Hugo", 4),
    ("Ulysses", "James Joyce", 3),
    ("Dubliners", "James Joyce", 5),
    ("The Trial", "Franz Kafka", 4),
    ("The Metamorphosis", "Franz Kafka", 6),
    ("The Castle", "Franz Kafka", 3),
    ("Lolita", "Vladimir Nabokov", 4),
    ("Pale Fire", "Vladimir Nabokov", 3),
    ("Beloved", "Toni Morrison", 5),
    ("Song of Solomon", "Toni Morrison", 4),
    ("Their Eyes Were Watching God", "Zora Neale Hurston", 5),
    ("Invisible Man", "Ralph Ellison", 4),
    ("The Sound and the Fury", "William Faulkner", 3),
    ("As I Lay Dying", "William Faulkner", 4),
    ("For Whom the Bell Tolls", "Ernest Hemingway", 5),
    ("A Farewell to Arms", "Ernest Hemingway", 6),
    ("The Sun Also Rises", "Ernest Hemingway", 4),
    ("The Old Man and the Sea", "Ernest Hemingway", 7),
    ("East of Eden", "John Steinbeck", 5),
    ("Cannery Row", "John Steinbeck", 4),
    ("Slaughterhouse-Five", "Kurt Vonnegut", 5),
    ("Cat's Cradle", "Kurt Vonnegut", 4),
    ("Breakfast of Champions", "Kurt Vonnegut", 3),
    ("The Bell Jar", "Sylvia Plath", 5),
    
    # Science Fiction (50 books)
    ("Dune", "Frank Herbert", 6),
    ("Dune Messiah", "Frank Herbert", 5),
    ("Children of Dune", "Frank Herbert", 4),
    ("Foundation", "Isaac Asimov", 7),
    ("Foundation and Empire", "Isaac Asimov", 6),
    ("Second Foundation", "Isaac Asimov", 5),
    ("I, Robot", "Isaac Asimov", 7),
    ("The Caves of Steel", "Isaac Asimov", 5),
    ("The Naked Sun", "Isaac Asimov", 4),
    ("Fahrenheit 451", "Ray Bradbury", 6),
    ("The Martian Chronicles", "Ray Bradbury", 5),
    ("Something Wicked This Way Comes", "Ray Bradbury", 4),
    ("2001: A Space Odyssey", "Arthur C. Clarke", 6),
    ("Childhood's End", "Arthur C. Clarke", 5),
    ("Rendezvous with Rama", "Arthur C. Clarke", 4),
    ("The Left Hand of Darkness", "Ursula K. Le Guin", 5),
    ("The Dispossessed", "Ursula K. Le Guin", 4),
    ("A Wizard of Earthsea", "Ursula K. Le Guin", 6),
    ("Neuromancer", "William Gibson", 5),
    ("Count Zero", "William Gibson", 4),
    ("Mona Lisa Overdrive", "William Gibson", 3),
    ("Snow Crash", "Neal Stephenson", 5),
    ("Cryptonomicon", "Neal Stephenson", 4),
    ("The Diamond Age", "Neal Stephenson", 3),
    ("Ender's Game", "Orson Scott Card", 7),
    ("Speaker for the Dead", "Orson Scott Card", 5),
    ("Xenocide", "Orson Scott Card", 4),
    ("Hyperion", "Dan Simmons", 5),
    ("The Fall of Hyperion", "Dan Simmons", 4),
    ("Endymion", "Dan Simmons", 3),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 8),
    ("The Restaurant at the End of the Universe", "Douglas Adams", 6),
    ("Life, the Universe and Everything", "Douglas Adams", 5),
    ("Starship Troopers", "Robert A. Heinlein", 5),
    ("Stranger in a Strange Land", "Robert A. Heinlein", 4),
    ("The Moon is a Harsh Mistress", "Robert A. Heinlein", 4),
    ("Do Androids Dream of Electric Sheep?", "Philip K. Dick", 6),
    ("The Man in the High Castle", "Philip K. Dick", 5),
    ("Ubik", "Philip K. Dick", 4),
    ("A Scanner Darkly", "Philip K. Dick", 4),
    ("Flowers for Algernon", "Daniel Keyes", 6),
    ("The Time Machine", "H.G. Wells", 7),
    ("The War of the Worlds", "H.G. Wells", 6),
    ("The Invisible Man", "H.G. Wells", 5),
    ("Twenty Thousand Leagues Under the Sea", "Jules Verne", 6),
    ("Journey to the Center of the Earth", "Jules Verne", 5),
    ("Around the World in Eighty Days", "Jules Verne", 6),
    ("Frankenstein", "Mary Shelley", 7),
    ("The Island of Doctor Moreau", "H.G. Wells", 5),
    ("Old Man's War", "John Scalzi", 4),
    
    # Fantasy (50 books)
    ("The Hobbit", "J.R.R. Tolkien", 9),
    ("The Fellowship of the Ring", "J.R.R. Tolkien", 8),
    ("The Two Towers", "J.R.R. Tolkien", 8),
    ("The Return of the King", "J.R.R. Tolkien", 8),
    ("The Silmarillion", "J.R.R. Tolkien", 5),
    ("A Game of Thrones", "George R.R. Martin", 7),
    ("A Clash of Kings", "George R.R. Martin", 6),
    ("A Storm of Swords", "George R.R. Martin", 6),
    ("A Feast for Crows", "George R.R. Martin", 5),
    ("A Dance with Dragons", "George R.R. Martin", 5),
    ("The Name of the Wind", "Patrick Rothfuss", 6),
    ("The Wise Man's Fear", "Patrick Rothfuss", 5),
    ("The Way of Kings", "Brandon Sanderson", 6),
    ("Words of Radiance", "Brandon Sanderson", 5),
    ("Oathbringer", "Brandon Sanderson", 4),
    ("Mistborn", "Brandon Sanderson", 6),
    ("The Well of Ascension", "Brandon Sanderson", 5),
    ("The Hero of Ages", "Brandon Sanderson", 4),
    ("Elantris", "Brandon Sanderson", 5),
    ("Warbreaker", "Brandon Sanderson", 4),
    ("The Eye of the World", "Robert Jordan", 6),
    ("The Great Hunt", "Robert Jordan", 5),
    ("The Dragon Reborn", "Robert Jordan", 5),
    ("The Shadow Rising", "Robert Jordan", 4),
    ("The Fires of Heaven", "Robert Jordan", 4),
    ("American Gods", "Neil Gaiman", 6),
    ("Good Omens", "Neil Gaiman & Terry Pratchett", 7),
    ("Neverwhere", "Neil Gaiman", 5),
    ("Stardust", "Neil Gaiman", 6),
    ("Coraline", "Neil Gaiman", 7),
    ("The Colour of Magic", "Terry Pratchett", 6),
    ("The Light Fantastic", "Terry Pratchett", 5),
    ("Equal Rites", "Terry Pratchett", 5),
    ("Mort", "Terry Pratchett", 6),
    ("Reaper Man", "Terry Pratchett", 5),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", 10),
    ("Harry Potter and the Chamber of Secrets", "J.K. Rowling", 9),
    ("Harry Potter and the Prisoner of Azkaban", "J.K. Rowling", 9),
    ("Harry Potter and the Goblet of Fire", "J.K. Rowling", 8),
    ("Harry Potter and the Order of the Phoenix", "J.K. Rowling", 8),
    ("Harry Potter and the Half-Blood Prince", "J.K. Rowling", 8),
    ("Harry Potter and the Deathly Hallows", "J.K. Rowling", 8),
    ("The Lion, the Witch and the Wardrobe", "C.S. Lewis", 8),
    ("Prince Caspian", "C.S. Lewis", 6),
    ("The Voyage of the Dawn Treader", "C.S. Lewis", 6),
    ("The Silver Chair", "C.S. Lewis", 5),
    ("The Horse and His Boy", "C.S. Lewis", 5),
    ("Eragon", "Christopher Paolini", 6),
    ("Eldest", "Christopher Paolini", 5),
    ("Brisingr", "Christopher Paolini", 4),
    
    # Mystery & Thriller (50 books)
    ("The Hound of the Baskervilles", "Arthur Conan Doyle", 7),
    ("A Study in Scarlet", "Arthur Conan Doyle", 6),
    ("The Sign of the Four", "Arthur Conan Doyle", 5),
    ("Murder on the Orient Express", "Agatha Christie", 8),
    ("And Then There Were None", "Agatha Christie", 7),
    ("The ABC Murders", "Agatha Christie", 6),
    ("Death on the Nile", "Agatha Christie", 6),
    ("The Murder of Roger Ackroyd", "Agatha Christie", 5),
    ("Rebecca", "Daphne du Maurier", 6),
    ("The Big Sleep", "Raymond Chandler", 5),
    ("Farewell, My Lovely", "Raymond Chandler", 4),
    ("The Maltese Falcon", "Dashiell Hammett", 5),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", 7),
    ("The Girl Who Played with Fire", "Stieg Larsson", 6),
    ("The Girl Who Kicked the Hornets' Nest", "Stieg Larsson", 5),
    ("Gone Girl", "Gillian Flynn", 7),
    ("Sharp Objects", "Gillian Flynn", 6),
    ("Dark Places", "Gillian Flynn", 5),
    ("The Da Vinci Code", "Dan Brown", 8),
    ("Angels and Demons", "Dan Brown", 7),
    ("Inferno", "Dan Brown", 6),
    ("Origin", "Dan Brown", 5),
    ("The Girl on the Train", "Paula Hawkins", 7),
    ("In the Woods", "Tana French", 5),
    ("The Likeness", "Tana French", 4),
    ("Big Little Lies", "Liane Moriarty", 6),
    ("The Secret History", "Donna Tartt", 5),
    ("The Goldfinch", "Donna Tartt", 4),
    ("In Cold Blood", "Truman Capote", 5),
    ("The Silence of the Lambs", "Thomas Harris", 5),
    ("Red Dragon", "Thomas Harris", 4),
    ("Hannibal", "Thomas Harris", 4),
    ("The No. 1 Ladies' Detective Agency", "Alexander McCall Smith", 5),
    ("Presumed Innocent", "Scott Turow", 4),
    ("The Firm", "John Grisham", 6),
    ("The Pelican Brief", "John Grisham", 5),
    ("A Time to Kill", "John Grisham", 6),
    ("The Client", "John Grisham", 5),
    ("The Rainmaker", "John Grisham", 4),
    ("Along Came a Spider", "James Patterson", 5),
    ("Kiss the Girls", "James Patterson", 4),
    ("Jack and Jill", "James Patterson", 4),
    ("Cat and Mouse", "James Patterson", 4),
    ("Pop Goes the Weasel", "James Patterson", 3),
    ("The Bourne Identity", "Robert Ludlum", 6),
    ("The Bourne Supremacy", "Robert Ludlum", 5),
    ("The Bourne Ultimatum", "Robert Ludlum", 5),
    ("Casino Royale", "Ian Fleming", 6),
    ("Live and Let Die", "Ian Fleming", 5),
    ("Moonraker", "Ian Fleming", 5),
    
    # Non-Fiction (50 books)
    ("Sapiens", "Yuval Noah Harari", 8),
    ("Homo Deus", "Yuval Noah Harari", 7),
    ("21 Lessons for the 21st Century", "Yuval Noah Harari", 6),
    ("A Brief History of Time", "Stephen Hawking", 8),
    ("The Universe in a Nutshell", "Stephen Hawking", 6),
    ("The Grand Design", "Stephen Hawking", 5),
    ("Cosmos", "Carl Sagan", 7),
    ("Pale Blue Dot", "Carl Sagan", 6),
    ("The Demon-Haunted World", "Carl Sagan", 5),
    ("Thinking, Fast and Slow", "Daniel Kahneman", 7),
    ("The Black Swan", "Nassim Nicholas Taleb", 6),
    ("Antifragile", "Nassim Nicholas Taleb", 5),
    ("Fooled by Randomness", "Nassim Nicholas Taleb", 5),
    ("Freakonomics", "Steven D. Levitt", 7),
    ("SuperFreakonomics", "Steven D. Levitt", 5),
    ("The Tipping Point", "Malcolm Gladwell", 7),
    ("Blink", "Malcolm Gladwell", 6),
    ("Outliers", "Malcolm Gladwell", 7),
    ("David and Goliath", "Malcolm Gladwell", 5),
    ("The Power of Habit", "Charles Duhigg", 7),
    ("Atomic Habits", "James Clear", 9),
    ("Deep Work", "Cal Newport", 7),
    ("Digital Minimalism", "Cal Newport", 6),
    ("So Good They Can't Ignore You", "Cal Newport", 5),
    ("Educated", "Tara Westover", 7),
    ("Becoming", "Michelle Obama", 8),
    ("The Diary of a Young Girl", "Anne Frank", 9),
    ("Long Walk to Freedom", "Nelson Mandela", 7),
    ("Steve Jobs", "Walter Isaacson", 7),
    ("Leonardo da Vinci", "Walter Isaacson", 6),
    ("Einstein: His Life and Universe", "Walter Isaacson", 5),
    ("The Wright Brothers", "David McCullough", 5),
    ("Alexander Hamilton", "Ron Chernow", 5),
    ("Grant", "Ron Chernow", 4),
    ("Team of Rivals", "Doris Kearns Goodwin", 5),
    ("The Art of War", "Sun Tzu", 9),
    ("Meditations", "Marcus Aurelius", 8),
    ("The Republic", "Plato", 7),
    ("Nicomachean Ethics", "Aristotle", 6),
    ("The Prince", "Niccolò Machiavelli", 7),
    ("Leviathan", "Thomas Hobbes", 5),
    ("The Wealth of Nations", "Adam Smith", 6),
    ("On the Origin of Species", "Charles Darwin", 7),
    ("The Selfish Gene", "Richard Dawkins", 7),
    ("The God Delusion", "Richard Dawkins", 6),
    ("Brief Answers to the Big Questions", "Stephen Hawking", 6),
    ("Astrophysics for People in a Hurry", "Neil deGrasse Tyson", 8),
    ("The Elegant Universe", "Brian Greene", 5),
    ("The Fabric of the Cosmos", "Brian Greene", 4),
    ("Surely You're Joking, Mr. Feynman!", "Richard Feynman", 7),
    
    # Self-Help & Personal Development (50 books)
    ("How to Win Friends and Influence People", "Dale Carnegie", 9),
    ("Think and Grow Rich", "Napoleon Hill", 8),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", 8),
    ("The Power of Now", "Eckhart Tolle", 7),
    ("A New Earth", "Eckhart Tolle", 6),
    ("Man's Search for Meaning", "Viktor Frankl", 8),
    ("The Alchemist", "Paulo Coelho", 9),
    ("The Monk Who Sold His Ferrari", "Robin Sharma", 7),
    ("Who Moved My Cheese?", "Spencer Johnson", 8),
    ("Rich Dad Poor Dad", "Robert T. Kiyosaki", 8),
    ("The 4-Hour Workweek", "Timothy Ferriss", 7),
    ("The Lean Startup", "Eric Ries", 6),
    ("Zero to One", "Peter Thiel", 7),
    ("Good to Great", "Jim Collins", 6),
    ("Built to Last", "Jim Collins", 5),
    ("Start with Why", "Simon Sinek", 7),
    ("Leaders Eat Last", "Simon Sinek", 6),
    ("The Infinite Game", "Simon Sinek", 5),
    ("Drive", "Daniel H. Pink", 6),
    ("To Sell Is Human", "Daniel H. Pink", 5),
    ("Emotional Intelligence", "Daniel Goleman", 7),
    ("Mindset", "Carol S. Dweck", 7),
    ("Grit", "Angela Duckworth", 6),
    ("The Gifts of Imperfection", "Brené Brown", 6),
    ("Daring Greatly", "Brené Brown", 5),
    ("Rising Strong", "Brené Brown", 5),
    ("The Subtle Art of Not Giving a F*ck", "Mark Manson", 8),
    ("Everything Is F*cked", "Mark Manson", 6),
    ("Can't Hurt Me", "David Goggins", 7),
    ("Extreme Ownership", "Jocko Willink", 6),
    ("The Obstacle Is the Way", "Ryan Holiday", 7),
    ("Ego Is the Enemy", "Ryan Holiday", 6),
    ("Stillness Is the Key", "Ryan Holiday", 6),
    ("12 Rules for Life", "Jordan B. Peterson", 7),
    ("Beyond Order", "Jordan B. Peterson", 5),
    ("The Road Less Travelled", "M. Scott Peck", 6),
    ("Awaken the Giant Within", "Tony Robbins", 6),
    ("Unlimited Power", "Tony Robbins", 5),
    ("The Magic of Thinking Big", "David J. Schwartz", 6),
    ("As a Man Thinketh", "James Allen", 7),
    ("The Richest Man in Babylon", "George S. Clason", 8),
    ("The Total Money Makeover", "Dave Ramsey", 6),
    ("I Will Teach You to Be Rich", "Ramit Sethi", 6),
    ("Your Money or Your Life", "Vicki Robin", 5),
    ("The Millionaire Next Door", "Thomas J. Stanley", 5),
    ("Psychology of Money", "Morgan Housel", 8),
    ("Principles", "Ray Dalio", 6),
    ("Shoe Dog", "Phil Knight", 7),
    ("Losing My Virginity", "Richard Branson", 5),
    ("Elon Musk", "Ashlee Vance", 7),
    
    # History (50 books)
    ("Guns, Germs, and Steel", "Jared Diamond", 7),
    ("The Collapse of Complex Societies", "Joseph Tainter", 4),
    ("The Rise and Fall of the Third Reich", "William L. Shirer", 5),
    ("The Second World War", "Winston Churchill", 5),
    ("Night", "Elie Wiesel", 8),
    ("The Hiding Place", "Corrie ten Boom", 6),
    ("Unbroken", "Laura Hillenbrand", 7),
    ("Band of Brothers", "Stephen E. Ambrose", 6),
    ("D-Day", "Stephen E. Ambrose", 5),
    ("The Guns of August", "Barbara W. Tuchman", 5),
    ("The Crusades Through Arab Eyes", "Amin Maalouf", 5),
    ("The Silk Roads", "Peter Frankopan", 6),
    ("SPQR: A History of Ancient Rome", "Mary Beard", 6),
    ("The History of the Peloponnesian War", "Thucydides", 5),
    ("Caesar", "Adrian Goldsworthy", 5),
    ("Napoleon", "Andrew Roberts", 5),
    ("Wellington", "Richard Holmes", 4),
    ("Churchill", "Roy Jenkins", 5),
    ("The Romanovs", "Simon Sebag Montefiore", 5),
    ("Peter the Great", "Robert K. Massie", 4),
    ("Catherine the Great", "Robert K. Massie", 4),
    ("The Ottoman Centuries", "Lord Kinross", 4),
    ("A People's History of the United States", "Howard Zinn", 6),
    ("The Federalist Papers", "Alexander Hamilton", 5),
    ("Common Sense", "Thomas Paine", 6),
    ("The Communist Manifesto", "Karl Marx", 7),
    ("Das Kapital", "Karl Marx", 5),
    ("The Origin of Totalitarianism", "Hannah Arendt", 5),
    ("The Gulag Archipelago", "Aleksandr Solzhenitsyn", 4),
    ("The Code Book", "Simon Singh", 6),
    ("The Information", "James Gleick", 5),
    ("Chaos", "James Gleick", 5),
    ("The Double Helix", "James D. Watson", 6),
    ("The Gene", "Siddhartha Mukherjee", 6),
    ("The Emperor of All Maladies", "Siddhartha Mukherjee", 5),
    ("Being Mortal", "Atul Gawande", 6),
    ("The Checklist Manifesto", "Atul Gawande", 5),
    ("Complications", "Atul Gawande", 5),
    ("The Body", "Bill Bryson", 7),
    ("A Short History of Nearly Everything", "Bill Bryson", 8),
    ("In a Sunburned Country", "Bill Bryson", 5),
    ("The Innovators", "Walter Isaacson", 6),
    ("The Second Machine Age", "Erik Brynjolfsson", 5),
    ("The Singularity Is Near", "Ray Kurzweil", 5),
    ("Life 3.0", "Max Tegmark", 5),
    ("Superintelligence", "Nick Bostrom", 5),
    ("Human Compatible", "Stuart Russell", 4),
    ("The Age of Surveillance Capitalism", "Shoshana Zuboff", 5),
    ("Weapons of Math Destruction", "Cathy O'Neil", 5),
    
    # Science & Technology (50 books)
    ("The Pragmatic Programmer", "David Thomas", 6),
    ("Clean Code", "Robert C. Martin", 7),
    ("The Clean Coder", "Robert C. Martin", 5),
    ("Design Patterns", "Gang of Four", 6),
    ("Introduction to Algorithms", "Cormen et al.", 6),
    ("The Art of Computer Programming", "Donald Knuth", 4),
    ("Structure and Interpretation of Computer Programs", "Abelson & Sussman", 5),
    ("Code Complete", "Steve McConnell", 5),
    ("Refactoring", "Martin Fowler", 5),
    ("Working Effectively with Legacy Code", "Michael C. Feathers", 4),
    ("The Interpretation of Dreams", "Sigmund Freud", 5),
    ("Beyond Good and Evil", "Friedrich Nietzsche", 6),
    ("Thus Spoke Zarathustra", "Friedrich Nietzsche", 5),
    ("The Will to Power", "Friedrich Nietzsche", 4),
    ("Being and Nothingness", "Jean-Paul Sartre", 4),
    ("The Second Sex", "Simone de Beauvoir", 5),
    ("The Divided Self", "R.D. Laing", 4),
    ("Games People Play", "Eric Berne", 6),
    ("I'm OK – You're OK", "Thomas A. Harris", 5),
    ("The Road to Character", "David Brooks", 5),
    ("Flow", "Mihaly Csikszentmihalyi", 6),
    ("Stumbling on Happiness", "Daniel Gilbert", 5),
    ("The Happiness Hypothesis", "Jonathan Haidt", 6),
    ("The Righteous Mind", "Jonathan Haidt", 5),
    ("Influence", "Robert B. Cialdini", 8),
    ("Pre-Suasion", "Robert B. Cialdini", 6),
    ("Predictably Irrational", "Dan Ariely", 7),
    ("The Paradox of Choice", "Barry Schwartz", 6),
    ("Quiet", "Susan Cain", 7),
    ("The Body Keeps the Score", "Bessel van der Kolk", 7),
    ("Why Zebras Don't Get Ulcers", "Robert M. Sapolsky", 5),
    ("Behave", "Robert M. Sapolsky", 5),
    ("The Lucifer Effect", "Philip Zimbardo", 5),
    ("Mistakes Were Made (But Not by Me)", "Carol Tavris", 5),
    ("Incognito", "David Eagleman", 6),
    ("The Brain That Changes Itself", "Norman Doidge", 6),
    ("Lost Connections", "Johann Hari", 6),
    ("Maybe You Should Talk to Someone", "Lori Gottlieb", 6),
    ("The Drama of the Gifted Child", "Alice Miller", 5),
    ("Running on Empty", "Jonice Webb", 5),
    ("Sense and Sensibility", "Jane Austen", 6),
    ("Emma", "Jane Austen", 6),
    ("Persuasion", "Jane Austen", 5),
    ("Northanger Abbey", "Jane Austen", 5),
    ("Gone with the Wind", "Margaret Mitchell", 6),
    ("The Notebook", "Nicholas Sparks", 7),
    ("A Walk to Remember", "Nicholas Sparks", 6),
    ("Message in a Bottle", "Nicholas Sparks", 5),
    ("The Bridges of Madison County", "Robert James Waller", 6),
    ("Outlander", "Diana Gabaldon", 6),
]

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── Init DB ──────────────────────────────────────────────────────────────────
def init_db():
    max_attempts = 5
    delay = 2

    for attempt in range(1, max_attempts + 1):
        try:
            cfg = DB_CONFIG.copy()
            cfg.pop('database')
            conn = mysql.connector.connect(**cfg)
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            conn.commit()
            conn.close()

            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT AUTO_INCREMENT PRIMARY KEY,
                    username   VARCHAR(100) UNIQUE NOT NULL,
                    password   VARCHAR(255) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS staff (
                    staff_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id  INT AUTO_INCREMENT PRIMARY KEY,
                    title    VARCHAR(255) NOT NULL,
                    author   VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()
            print(f"Database initialised successfully on attempt {attempt}.")
            return
        except mysql.connector.Error as e:
            print(f"DB init attempt {attempt}/{max_attempts} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay)

    print("Warning: could not initialise the database after "
          f"{max_attempts} attempts. The app will start anyway.")

# ── Lazy DB Init ─────────────────────────────────────────────────────────────
@app.before_request
def ensure_db():
    global _db_initialised
    if not _db_initialised:
        init_db()
        _db_initialised = True

# ── Admin Route: Clear and Insert 500 Books ──────────────────────────────────
@app.route('/admin/insert-500-books')
def insert_500_books():
    """Clear existing books and insert all 500 books"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Clear existing books
        cur.execute("DELETE FROM books")
        conn.commit()
        
        # Insert all 500 books
        inserted = 0
        for title, author, quantity in BOOKS_DATA:
            try:
                cur.execute(
                    "INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)",
                    (title, author, quantity)
                )
                inserted += 1
            except mysql.connector.Error:
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'✅ Successfully inserted {inserted} books into the database!',
            'books_count': inserted,
            'categories': '50 Classic Literature, 50 Sci-Fi, 50 Fantasy, 50 Mystery, 50 Non-Fiction, 50 Self-Help, 50 History, 50 Science, 50 Psychology, 50 Romance'
        }), 200
        
    except mysql.connector.Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500

# ── Auth Routes ──────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        role     = request.form['role']
        table    = 'students' if role == 'student' else 'staff'
        id_col   = 'student_id' if role == 'student' else 'staff_id'

        try:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)
            cur.execute(f"SELECT * FROM {table} WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                session['user']     = username
                session['role']     = role
                session['user_id']  = user[id_col]
                return redirect(url_for('student_dashboard' if role == 'student' else 'staff_dashboard'))
            flash('Invalid credentials. Please try again.')
        except mysql.connector.Error as e:
            flash(f'Database error: unable to process login. Please try again later.')
            app.logger.error(f'Login DB error: {e}')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        role     = request.form['role']
        table    = 'students' if role == 'student' else 'staff'

        conn = None
        try:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute(f"INSERT INTO {table} (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists. Choose another.')
        except mysql.connector.Error as e:
            flash('Database error: unable to complete registration. Please try again later.')
            app.logger.error(f'Register DB error: {e}')
        finally:
            if conn:
                conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Student Routes ───────────────────────────────────────────────────────────
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', user=session['user'])

@app.route('/student/books')
def student_books():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        if query:
            cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s",
                        (f'%{query}%', f'%{query}%'))
        else:
            cur.execute("SELECT * FROM books ORDER BY title")
        books = cur.fetchall()
        conn.close()
    except mysql.connector.Error as e:
        flash('Database error: unable to retrieve books. Please try again later.')
        app.logger.error(f'Student books DB error: {e}')
        books = []
    return render_template('books.html', books=books, query=query, role='student')

# ── Staff Routes ─────────────────────────────────────────────────────────────
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    try:
        conn  = get_db()
        cur   = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS total FROM books")
        stats = cur.fetchone()
        conn.close()
    except mysql.connector.Error as e:
        flash('Database error: unable to load dashboard stats. Please try again later.')
        app.logger.error(f'Staff dashboard DB error: {e}')
        stats = {'total': 'N/A'}
    return render_template('staff_dashboard.html', user=session['user'], stats=stats)

@app.route('/staff/books')
def staff_books():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        if query:
            cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s",
                        (f'%{query}%', f'%{query}%'))
        else:
            cur.execute("SELECT * FROM books ORDER BY title")
        books = cur.fetchall()
        conn.close()
    except mysql.connector.Error as e:
        flash('Database error: unable to retrieve books. Please try again later.')
        app.logger.error(f'Staff books DB error: {e}')
        books = []
    return render_template('books.html', books=books, query=query, role='staff')

@app.route('/staff/add_book', methods=['GET', 'POST'])
def add_book():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title    = request.form['title'].strip()
        author   = request.form['author'].strip()
        quantity = int(request.form['quantity'])
        try:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)",
                        (title, author, quantity))
            conn.commit()
            conn.close()
            flash('Book added successfully!')
            return redirect(url_for('staff_books'))
        except mysql.connector.Error as e:
            flash('Database error: unable to add book. Please try again later.')
            app.logger.error(f'Add book DB error: {e}')
    return render_template('add_book.html')

@app.route('/staff/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    conn = None
    try:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        if request.method == 'POST':
            title    = request.form['title'].strip()
            author   = request.form['author'].strip()
            quantity = int(request.form['quantity'])
            cur.execute("UPDATE books SET title=%s, author=%s, quantity=%s WHERE book_id=%s",
                        (title, author, quantity, book_id))
            conn.commit()
            conn.close()
            flash('Book updated successfully!')
            return redirect(url_for('staff_books'))
        cur.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
        book = cur.fetchone()
        conn.close()
    except mysql.connector.Error as e:
        flash('Database error: unable to edit book. Please try again later.')
        app.logger.error(f'Edit book DB error: {e}')
        if conn:
            conn.close()
        return redirect(url_for('staff_books'))
    return render_template('add_book.html', book=book, edit=True)

@app.route('/staff/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
        conn.commit()
        conn.close()
        flash('Book deleted.')
    except mysql.connector.Error as e:
        flash('Database error: unable to delete book. Please try again later.')
        app.logger.error(f'Delete book DB error: {e}')
    return redirect(url_for('staff_books'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

