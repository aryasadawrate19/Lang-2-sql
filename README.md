# Lang-2-SQL 🤖
**A Streamlit-powered Natural Language to SQL Converter with Database Chat Assistant**

Convert natural language questions into SQL queries and interact with your databases through an intuitive chat interface powered by Google's Gemini AI.

---

## 🌟 Features

### 🔐 **User Authentication**
- Secure user registration and login system
- Session management with tokens
- Password hashing for security

### 💬 **Interactive Chat Interface** 
- Real-time conversation with AI assistant
- Chat history and management
- Multiple chat sessions per user

### 🗄️ **Multi-Database Support**
- Connect to MySQL, PostgreSQL, and SQLite databases
- Save and manage multiple database connections
- Test connections before saving

### 🧠 **AI-Powered Query Generation**
- Natural language to SQL conversion using Google Gemini
- Context-aware responses based on chat history
- Database schema understanding

### 📊 **Query History & Analytics**
- Track all generated queries and results
- View query history by chat session
- Export and analyze database interactions

---

## 🏗️ Project Architecture

```
Lang-2-sql/
├── app.py              # Main Streamlit application
├── modules/
│   ├── auth.py         # User authentication & session management
│   ├── chat.py         # Chat interface & AI response handling
│   ├── db.py           # Database connection management
│   ├── db_setup.py     # Database schema creation
│   ├── db_utils.py     # Database utility functions
│   ├── nav.py          # Navigation & URL routing
│   └── query.py        # Query tracking & history
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL/PostgreSQL database for app data storage
- Google Gemini API key
- Target databases to query (MySQL, PostgreSQL, or SQLite)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aryasadawrate19/Lang-2-sql.git
cd Lang-2-sql
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Application Database (for storing users, chats, etc.)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306
DB_NAME=lang2sql
```

5. **Database Setup**
```bash
# Create the application database
mysql -u root -p -e "CREATE DATABASE lang2sql;"
```

6. **Run the application**
```bash
streamlit run app.py
```

---

## 📖 Usage Guide

### 1. **User Registration/Login**
- Navigate to the registration page to create an account
- Login with your credentials to access the chat interface

### 2. **Database Connection**
- Go to "Databases" in the sidebar
- Add your database connection details
- Test the connection before saving

### 3. **Start Chatting**
- Select a database from the sidebar
- Create a new chat or continue an existing one
- Ask questions in natural language:
  - *"Show me all customers from New York"*
  - *"What are the top 10 products by sales?"*
  - *"List all tables in the database"*

### 4. **View History**
- Check the "History" section to review past queries
- See generated SQL and results for each question

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Backend** | Python |
| **AI Engine** | Google Gemini 2.0 Flash |
| **Database ORM** | SQLAlchemy, LangChain SQLDatabase |
| **Authentication** | Custom session-based auth |
| **Database Drivers** | mysql-connector-python, psycopg2 |

---

## 📋 Dependencies

```txt
streamlit>=1.28.0
google-generativeai>=0.3.0
mysql-connector-python>=8.0.0
langchain-community>=0.0.20
langchain-core>=0.1.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
```

---

## 🔒 Security Features

- **Password Hashing**: SHA-256 encryption for user passwords
- **Session Tokens**: Secure UUID-based session management  
- **Input Validation**: SQL injection prevention through parameterized queries
- **Database Isolation**: Separate application and query databases

---

## 🎯 Example Interactions

**User Input:** *"Show me the revenue by month"*
```sql
-- Generated SQL:
SELECT 
    MONTH(order_date) as month,
    SUM(total_amount) as revenue 
FROM orders 
GROUP BY MONTH(order_date)
ORDER BY month;
```

**User Input:** *"Who are my top 5 customers?"*
```sql
-- Generated SQL:
SELECT 
    customer_name,
    SUM(total_amount) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 5;
```

---

## 🚧 Roadmap

- [ ] Support for more database types (Oracle, MongoDB)
- [ ] Export query results to CSV/Excel
- [ ] Advanced query optimization suggestions
- [ ] Team collaboration features
- [ ] API endpoints for external integration
- [ ] Custom AI model training on your schema

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Troubleshooting

### Common Issues:

**Database Connection Failed**
- Verify your database credentials in `.env`
- Ensure the database server is running
- Check firewall settings

**Gemini API Errors**
- Verify your `GEMINI_API_KEY` in `.env`
- Check API quota and billing status
- Ensure API key has proper permissions

**Module Import Errors**
- Activate your virtual environment
- Install all requirements: `pip install -r requirements.txt`

---

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/aryasadawrate19/Lang-2-sql/issues)
- **Documentation**: Check the code comments for detailed implementation notes

---

**Made with ❤️ by [Arya Sadawrate](https://github.com/aryasadawrate19)**
