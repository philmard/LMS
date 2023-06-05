import mysql.connector, datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, session
from itertools import count
from datetime import timedelta
from school_lib import app,connection


# Function to authenticate user
def authenticate_user(username, password):
    # Connect to the database
    try:
        cursor = connection.cursor()

        # Query to check if username and password match
        query = "SELECT COUNT(*), user_type, user_id, school_id FROM `user` WHERE username = %s AND password = %s AND user_status = 1"
        cursor.execute(query, (username, password))

        # Fetch the result
        result = cursor.fetchall()
        count = result[0][0]
        user_type = result[0][1]
        user_id = result[0][2]
        school_id = result[0][3]

        # Close the database connection
        cursor.close()

        # Return True if username and password match, False otherwise
        return count == 1, user_type, user_id, school_id

    except mysql.connector.Error as err:
        print("Database Error: {}".format(err))

    # Return False in case of any error
    return False #?

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_post', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    result, user_type, user_id, school_id = authenticate_user(username, password) # if result==1 then count was 1.
    if result:
        # Store user information in the session
        session['username'] = username
        session['user_type'] = user_type
        session['user_id'] = user_id
        session['school_id'] = school_id
        return redirect('/home')
    else:
        error = 'Invalid username or password'
        return render_template('login.html', error=error)
    
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup_post', methods=['POST'])
def signup_post():
    try:
        # Retrieve the form data from the request object
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_type = request.form['user_type']
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        school_id = request.form['school_id']
        age = request.form['age']
        user_status = 0

        cursor = connection.cursor()

        # Execute the SQL query
        query = f"""
        INSERT INTO `user` (username, password, email, user_type, last_name, first_name, school_id, age, user_status)
        VALUES ('{username}', '{password}', '{email}', '{user_type}', '{last_name}', '{first_name}', '{school_id}', '{age}', '{user_status}')
        """
        cursor.execute(query)

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and database connection
        cursor.close()
        connection.close()

        # Redirect to the login page or any other desired page
        return "Successful signup!"
    except Exception as e:
        # Handle the exception appropriately (e.g., log the error, show an error message)
        return "An error occurred during signup: " + str(e)




@app.route('/home')
def home():
    # Check if the user is logged in
    if 'username' in session and ((session['user_type'] == 1) or (session['user_type'] == 0)):
        return render_template('home1.html', username=session['username'], user_type=session['user_type'])
    elif 'username' in session and session['user_type'] == 2:
        return render_template('home2.html', username=session['username'])
    elif 'username' in session and session['user_type'] == 3:
        return render_template('home3.html', username=session['username'])
    else:
        return redirect('/')

@app.route('/fetch_category_books', methods=['GET'])
def fetch_category_books():
    try:
        category = request.args.get('category')
        cursor = connection.cursor()

        query = f"""
            SELECT c.category_name, GROUP_CONCAT(DISTINCT a.author_name SEPARATOR ',') AS authors,
            (
            SELECT GROUP_CONCAT(DISTINCT CONCAT(u.first_name, ' ', u.last_name) SEPARATOR ',')
            FROM book b
            JOIN transaction t ON b.ISBN = t.ISBN
            JOIN `user` u ON t.user_id = u.user_id
            JOIN book_category bc ON b.ISBN = bc.ISBN
            WHERE bc.category_id = c.category_id
            AND u.user_type = 1
            AND t.transaction_type = 1
            AND t.date_of_borrowing >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            ) AS users
            FROM category c
            JOIN book_category bc ON c.category_id = bc.category_id
            JOIN book_author ba ON bc.ISBN = ba.ISBN
            JOIN author a ON ba.author_id = a.author_id
            WHERE 1=1
            """
        if category:
            query+= f" AND c.category_name LIKE '%{category}%'"

        query+= "GROUP BY c.category_name;"                           
                      
        cursor.execute(query)
        
        books = cursor.fetchall()

        cursor.close()

        return render_template('category_results.html', books=books)

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/fetch_school_loans', methods=['GET'])
def fetch_school_loans():
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        cursor = connection.cursor()

        query = """
            SELECT s.name, COUNT(t.transaction_id) AS loan_count
            FROM school s
            JOIN user u ON s.school_id = u.school_id
            JOIN `transaction` t ON u.user_id = t.user_id
            WHERE 1=1
            """
        if year:
            query += f"AND YEAR(t.date_of_borrowing) = {year} "
        if month:
            query += f"AND MONTH(t.date_of_borrowing) = {month} "
            
        query += "GROUP BY s.name"

        cursor.execute(query)

        loans = cursor.fetchall()

        cursor.close()

        return render_template('year_month_results.html', loans=loans)

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/fetch_young_teachers', methods=['GET'])
def fetch_young_teachers():
    try:
        cursor = connection.cursor()

        query = """
            SELECT u.first_name, u.last_name, COUNT(t.transaction_id) AS num_borrowed_books
            FROM `user` u
            JOIN `transaction` t ON u.user_id = t.user_id
            WHERE u.user_type = 1 AND u.age < 40 AND t.transaction_type = 1
            GROUP BY u.user_id
            ORDER BY num_borrowed_books DESC
            LIMIT 10;
        """

        cursor.execute(query)

        young_teachers = cursor.fetchall()

        cursor.close()

        return render_template('young_teachers.html', young_teachers=young_teachers)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

@app.route('/fetch_zero_borrow_authors', methods=['GET'])
def fetch_zero_borrow_authors():
    try:
        cursor = connection.cursor()

        query = """
            SELECT a.author_id, a.author_name
            FROM author a
            LEFT JOIN book_author ba ON a.author_id = ba.author_id
            LEFT JOIN book b ON ba.ISBN = b.ISBN
            LEFT JOIN transaction t ON b.ISBN = t.ISBN
            GROUP BY a.author_id, a.author_name
            HAVING COUNT(t.ISBN) = 0;
        """

        cursor.execute(query)

        zero_borrow_authors = cursor.fetchall()

        cursor.close()

        return render_template('zero_borrow_authors.html', zero_borrow_authors=zero_borrow_authors)

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/fetch_operators_same_borrows', methods=['GET'])
def fetch_operators_same_borrows():
    try:
        cursor = connection.cursor()

        query = """
            SELECT DISTINCT subquery.first_name, subquery.last_name, subquery.transaction_count
            FROM (
            SELECT s.school_id, s.name, COUNT(t.transaction_id) AS transaction_count, u2.first_name, u2.last_name
            FROM school s
            LEFT JOIN `user` u ON s.school_id = u.school_id
            LEFT JOIN `transaction` t ON u.user_id = t.user_id
            LEFT JOIN `user` u2 ON s.school_id = u2.school_id AND u2.user_type = '2'
            WHERE t.transaction_type = 1
            GROUP BY s.school_id, s.name, u2.first_name, u2.last_name
            HAVING COUNT(t.transaction_id) > 20
            ) AS subquery
            INNER JOIN (
            SELECT transaction_count
            FROM (
            SELECT COUNT(t.transaction_id) AS transaction_count
            FROM school s
            LEFT JOIN `user` u ON s.school_id = u.school_id
            LEFT JOIN `transaction` t ON u.user_id = t.user_id
            WHERE t.transaction_type = 1
            AND t.date_of_borrowing >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) -- interval of 1 year
            GROUP BY s.school_id, s.name
            ) AS count_subquery
            GROUP BY transaction_count
            HAVING COUNT(transaction_count) > 1 -- more than 1 occurence
            ) AS count_join ON subquery.transaction_count = count_join.transaction_count;
        """

        cursor.execute(query)

        operators_same_borrows = cursor.fetchall()

        cursor.close()

        return render_template('operators_same_borrows.html', operators_same_borrows=operators_same_borrows)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/fetch_top_category_pairs', methods=['GET'])
def fetch_top_category_pairs():
    try:
        cursor = connection.cursor()

        query = """
            SELECT c1.category_name AS category1, c2.category_name AS category2, COUNT(*) AS borrow_count
            FROM book_category bc1
            JOIN book_category bc2 ON bc1.ISBN = bc2.ISBN AND bc1.category_id < bc2.category_id
            JOIN category c1 ON bc1.category_id = c1.category_id
            JOIN category c2 ON bc2.category_id = c2.category_id
            JOIN transaction t ON t.ISBN = bc1.ISBN
            WHERE t.transaction_type = 1
            GROUP BY c1.category_id, c2.category_id
            ORDER BY borrow_count DESC
            LIMIT 3;
        """

        cursor.execute(query)

        top_category_pairs = cursor.fetchall()

        cursor.close()

        return render_template('top_category_pairs.html', top_category_pairs=top_category_pairs)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/fetch_authors_less_5', methods=['GET'])
def fetch_authors_less_5():
    try:
        cursor = connection.cursor()

        query = """
            SELECT a.author_id, a.author_name, COUNT(ba.book_author_id) AS num_books
			FROM author a
			JOIN book_author ba ON a.author_id = ba.author_id
			GROUP BY a.author_id, a.author_name
			HAVING num_books <= (
			SELECT COUNT(book_author_id)
			FROM book_author
			GROUP BY author_id
			ORDER BY COUNT(book_author_id) DESC
			LIMIT 1
			) - 5;
        """

        cursor.execute(query)

        authors_less_5 = cursor.fetchall()

        cursor.close()

        return render_template('authors_less_5.html', authors_less_5=authors_less_5)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

@app.route('/fetch_signups2', methods=['GET'])
def fetch_signups2():
    try:
        cursor = connection.cursor()

        # Query the database to fetch the additional details of the book
        query = """
            SELECT u.username, u.user_type, u.email, u.last_name, u.first_name, u.user_id, u.school_id, u.age, u.user_status
            FROM user u
            WHERE u.user_type = 2 
        """
        cursor.execute(query)
        user_details = cursor.fetchall()
        cursor.close()

        return render_template('fetch_signups2.html', user_details=user_details)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/accept_signups2', methods=['POST'])
def accept_signups2():
    try:
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        cursor = connection.cursor()
        if action == 'Cancel user':
            query = """
            UPDATE `user`
            SET user_status = 1
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            connection.commit()

        elif action == 'Accept user':
            query = """
            UPDATE `user`
            SET user_status = 0
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            connection.commit()


        return redirect('fetch_signups2')
    except Exception as e:
        print('Error:', e)
        return Response(status=204)


#logging.basicConfig(level=logging.DEBUG)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate the form inputs
        if not current_password or not new_password or not confirm_password:
            return "Please fill in all the fields."

        # Check if the new password and confirm password match
        if new_password != confirm_password:
            return "New password and confirm password do not match."

        # Get the user's current password from the database
        cursor = connection.cursor()
        query = """
        SELECT password
        FROM `user`
        WHERE user_id = %s
        """
        cursor.execute(query, (session['user_id'],))
        result = cursor.fetchone()

        if not result:
            return "User not found."

        stored_password = result[0]

        # Compare the stored password with the entered current password
        #hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
        #stored_password_hashed = hashlib.sha256(stored_password.encode()).hexdigest()

        #logging.debug("current_password: %s", current_password)
        #logging.debug("hashed_current_password: %s", current_password)
        #logging.debug("stored_password: %s", stored_password)

        if current_password != stored_password:
            return "Invalid current password."

        # Hash the new password and update it in the database
        #hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
        query = """
        UPDATE `user`
        SET password = %s
        WHERE user_id = %s
        """
        cursor.execute(query, (new_password, session['user_id']))
        connection.commit()
        cursor.close()

        return "Password changed successfully."

    return render_template('change_password.html')





@app.route('/fetch_title_author', methods=['GET'])
def fetch_title_author():
    try:
        author = request.args.get('author')
        category = request.args.get('category')
        title = request.args.get('title')
        copies_criteria = request.args.get('copies_criteria') # 4o
        cursor = connection.cursor()

        query = """
            SELECT b.ISBN, b.title, GROUP_CONCAT(DISTINCT a.author_name) AS authors, GROUP_CONCAT(DISTINCT c.category_name) AS categories, b.num_copies
            FROM book b
            LEFT JOIN book_author ba ON b.ISBN = ba.ISBN
            LEFT JOIN author a ON ba.author_id = a.author_id
            LEFT JOIN book_category bc ON b.ISBN = bc.ISBN
            LEFT JOIN category c ON bc.category_id = c.category_id
            LEFT JOIN `transaction` t ON b.ISBN = t.ISBN
            WHERE b.ISBN IN (
            SELECT ba.ISBN
            FROM book_author ba
            INNER JOIN author a ON ba.author_id = a.author_id 
            """

        if author:
            query += f" AND a.author_name LIKE '%{author}%'"

        query += " ) AND b.ISBN IN (SELECT bc.ISBN FROM book_category bc INNER JOIN category c ON bc.category_id = c.category_id"

        if category:
            query += f" AND c.category_name LIKE '%{category}%'"

        query += ")"

        if title:
            query += f" AND b.title LIKE '%{title}%'"
        
        if copies_criteria:
            query += f" AND b.num_copies >= '{copies_criteria}'" # check if this works

        query += " GROUP BY b.ISBN;"


        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return render_template('title_author_results.html', results=results)

    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/book_details', methods=['GET'])
def book_details():
    try:
        ISBN = request.args.get('ISBN')  # Retrieve the ISBN of the book

        cursor = connection.cursor()

        # Query the database to fetch the additional details of the book
        query = """
            SELECT b.title, b.publisher, b.num_pages, b.images, b.language, b.summary, b.num_copies, b.ISBN
            FROM book b
            WHERE b.ISBN = %s
        """
        cursor.execute(query, (ISBN,))
        book_details = cursor.fetchone()
        cursor.close()

        return render_template('book_details.html', book_details=book_details)

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/edit_book', methods=['GET', 'POST'])
def edit_book():
    if request.method == 'GET':
        try:
            ISBN = request.args.get('ISBN')  # Retrieve the ISBN of the book
            
            # Fetch the existing book details from the database
            cursor = connection.cursor()
            query = """
                SELECT title, publisher, num_pages, images, language, summary, num_copies, ISBN
                FROM book
                WHERE ISBN = %s
            """
            cursor.execute(query, (ISBN,))
            book_details = cursor.fetchone()
            cursor.close()

            return render_template('edit_book.html', book_details=book_details)

        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    elif request.method == 'POST':
        try:
            ISBN = request.form.get('ISBN')
            title = request.form.get('title')
            publisher = request.form.get('publisher')
            num_pages = request.form.get('num_pages')
            language = request.form.get('language')
            summary = request.form.get('summary')
            num_copies = request.form.get('num_copies')
            
            # Update the book details in the database
            cursor = connection.cursor()
            query = """
                UPDATE book
                SET title = %s, publisher = %s, num_pages = %s, language = %s, summary = %s, num_copies = %s
                WHERE ISBN = %s
            """
            cursor.execute(query, (title, publisher, num_pages, language, summary, num_copies, ISBN))
            connection.commit()
            cursor.close()

            return "Book details updated successfully!"

        except Exception as e:
            return f"An error occurred: {str(e)}"


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            school_id = session['school_id']
            ISBN = request.form['ISBN']  # Get the ISBN input from the form
            title = request.form['title']
            author = request.form['author']
            category = request.form['category']
            copies = int(request.form['copies'])
            publisher = request.form['publisher']
            num_pages = int(request.form['num_pages'])
            summary = request.form['summary']
            images = request.form['images']
            language = request.form['language']
         
            # Insert the new book into the database
            cursor = connection.cursor()
            
            select_duplicate_ISBN_query = f"""
                SELECT ISBN
                FROM book
                WHERE ISBN = '{ISBN}'
            """
            cursor.execute(select_duplicate_ISBN_query)
            duplicate_ISBN_result = cursor.fetchone()
            if duplicate_ISBN_result is None:
                insert_query = f"""
                INSERT INTO book (ISBN, title, num_copies, publisher, num_pages, summary, images, language)
                VALUES ('{ISBN}', '{title}', '{copies}', '{publisher}', '{num_pages}', '{summary}', '{images}', '{language}')
                """
                cursor.execute(insert_query)
            
                school_book_id = cursor.lastrowid
                insert_school_book_query = f"""
                INSERT INTO school_book(ISBN, school_id, school_book_id)
                VALUES ('{ISBN}', '{school_id}', '{school_book_id}')
                """
                cursor.execute(insert_school_book_query)

                # Insert the author into the database if it doesn't exist already
                select_author_query = f"""
                SELECT author_id
                FROM author
                WHERE author_name = '{author}'
                """
                cursor.execute(select_author_query)
                author_result = cursor.fetchone()
                if author_result is None:
                    insert_author_query = f"""
                    INSERT INTO author (author_name)
                    VALUES ('{author}')
                    """
                    cursor.execute(insert_author_query)
                    author_id = cursor.lastrowid
                else:
                    author_id = author_result[0]
            
                # Insert the book-author relationship into the database
                insert_book_author_query = f"""
                INSERT INTO book_author (ISBN, author_id)
                VALUES ('{ISBN}', '{author_id}')
                """
                cursor.execute(insert_book_author_query)
            
                # Insert the category into the database if it doesn't exist already
                select_category_query = f"""
                SELECT category_id
                FROM category
                WHERE category_name = '{category}'
                """
                cursor.execute(select_category_query)
                category_result = cursor.fetchone()
                if category_result is None:
                    insert_category_query = f"""
                    INSERT INTO category (category_name)
                    VALUES ('{category}')
                    """
                    cursor.execute(insert_category_query)
                    category_id = cursor.lastrowid
                else:
                    category_id = category_result[0]
            
                # Insert the book-category relationship into the database
                insert_book_category_query = f"""
                INSERT INTO book_category (ISBN, category_id)
                VALUES ('{ISBN}', '{category_id}')
                """
                cursor.execute(insert_book_category_query)
            
                connection.commit()
                cursor.close()
            
                return redirect(url_for('fetch_title_author'))
            else:
                return "book already exists"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template('add_book.html')

@app.route('/fetch_delayed_returns', methods=['GET'])
def fetch_delayed_returns():
    try:
        first_name = request.args.get('first_name')  
        last_name = request.args.get('last_name')  
        delayed_days = request.args.get('delayed_days')  
        cursor = connection.cursor()

        # Construct the base query
        query = """
            SELECT 
            t.`user_id`,
            u.`username`,
            u.`first_name`,
            u.`last_name`,
            DATEDIFF(CURRENT_TIMESTAMP(), t.`date_of_max_return`) AS delayed_days
            FROM `transaction` t
            JOIN `user` u ON t.`user_id` = u.`user_id`
            WHERE t.`transaction_type` = 1
            AND t.`transaction_status` = 1
            AND CURRENT_TIMESTAMP() > t.`date_of_max_return`
  
        """

        # Add conditions to the query based on the provided search criteria
        if first_name:
            query += f" AND u.`first_name` LIKE '%{first_name}%'"
        if last_name:
            query += f" AND u.`last_name` LIKE '%{last_name}%'"
        if delayed_days:
            query += f" AND DATEDIFF(CURRENT_TIMESTAMP(), t.`date_of_max_return`) >= {delayed_days}"

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return render_template('delayed_days_results.html', results=results)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/fetch_average_ratings', methods=['GET'])
def fetch_average_ratings():
    try:
        username = request.args.get('username')  
        category = request.args.get('category')   
        cursor = connection.cursor()

        # Construct the base query
        query = """
            SELECT r.user_id, u.username, c.category_name, AVG(r.likert_rating) AS average_rating
            FROM review r
            JOIN book b ON r.ISBN = b.ISBN
            JOIN book_category bc ON bc.ISBN = b.ISBN
            JOIN category c ON c.category_id = bc.category_id
            JOIN user u ON u.user_id = r.user_id
            WHERE 1 = 1
        """

        # Add conditions to the query based on the provided search criteria
        if username:
            query += f" AND u.`username` LIKE '%{username}%'"
        if category:
            query += f" AND c.`category_name` LIKE '%{category}%'"

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        case = 0  # Default case: No input provided

        if username and category:
            case = 3  # Case 3: Both username and category provided
        elif username:
            case = 1  # Case 1: Only username provided
        elif category:
            case = 2  # Case 2: Only category provided

        return render_template('average_ratings.html', results=results, case=case)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/fetch_signups01', methods=['GET'])
def fetch_signups01():
    try:
        cursor = connection.cursor()

        # Query the database to fetch the additional details of the book
        query = """
            SELECT u.username, u.user_type, u.email, u.last_name, u.first_name, u.user_id, u.school_id, u.age, u.user_status
            FROM user u
            WHERE u.user_type IN (0,1) 
        """
        cursor.execute(query)
        user_details = cursor.fetchall()
        cursor.close()

        return render_template('fetch_signups01.html', user_details=user_details)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/accept_signups01', methods=['POST'])
def accept_signups01():
    try:
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        cursor = connection.cursor()
        if action == 'Cancel user':
            query = """
            UPDATE `user`
            SET user_status = 1
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            connection.commit()

        elif action == 'Accept user':
            query = """
            UPDATE `user`
            SET user_status = 0
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            connection.commit()


        return redirect('fetch_signups01')
    except Exception as e:
        print('Error:', e)
        return Response(status=204)



# Delete a user

@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        user_id = request.form.get('user_id')
        # Execute the delete query
        query = "DELETE FROM `user` WHERE user_id = %s"
        cursor = connection.cursor()
        cursor.execute(query, (user_id,))
        connection.commit()
        return "User deleted successfully"

    except Exception as e:
        print('Error:', e)
        return Response(status=204)



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = connection.cursor()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        age = request.form.get('age')
        school_id = request.form.get('school_id')

        query = """
        UPDATE `user`
        SET username = %s, email = %s, age = %s, school_id = %s
        WHERE user_id = %s AND user_type = 1
        """
        cursor.execute(query, (username, email, age, school_id, user_id))
        connection.commit()

    query = """
    SELECT username, email, age, school_id
    FROM `user`
    WHERE user_id = %s AND user_type = 1
    """
    cursor.execute(query, (user_id,))
    user_info = cursor.fetchone()

    cursor.close()

    return render_template('profile.html', user_info=user_info)



@app.route('/fetch_all_books', methods=['GET'])
def fetch_all_books():
    try:
        author = request.args.get('author')
        category = request.args.get('category')
        title = request.args.get('title')
        cursor = connection.cursor()

        query = """
            SELECT b.ISBN, b.title, GROUP_CONCAT(DISTINCT a.author_name) AS authors, GROUP_CONCAT(DISTINCT c.category_name) AS categories,
            IF(t.transaction_type = 0, 0, 1) AS transaction_type1,
            IF(t.transaction_type = 1, 1, 2) AS transaction_type2
            FROM book b
            LEFT JOIN book_author ba ON b.ISBN = ba.ISBN
            LEFT JOIN author a ON ba.author_id = a.author_id
            LEFT JOIN book_category bc ON b.ISBN = bc.ISBN
            LEFT JOIN category c ON bc.category_id = c.category_id
            LEFT JOIN `transaction` t ON b.ISBN = t.ISBN AND t.user_id = %s
            WHERE b.ISBN IN (
            SELECT ba.ISBN
            FROM book_author ba
            INNER JOIN author a ON ba.author_id = a.author_id 
            """

        if author:
            query += " AND a.author_name LIKE %s"

        query += " ) AND b.ISBN IN (SELECT bc.ISBN FROM book_category bc INNER JOIN category c ON bc.category_id = c.category_id"

        if category:
            query += " AND c.category_name LIKE %s"

        query += ")"

        if title:
            query += " AND b.title LIKE %s"

        query += " GROUP BY b.ISBN, b.title"

        if author and category and title:
            cursor.execute(query, (session['user_id'], f"%{author}%", f"%{category}%", f"%{title}%"))
        elif author and category:
            cursor.execute(query, (session['user_id'], f"%{author}%", f"%{category}%"))
        elif author and title:
            cursor.execute(query, (session['user_id'], f"%{author}%", f"%{title}%"))
        elif category and title:
            cursor.execute(query, (session['user_id'], f"%{category}%", f"%{title}%"))
        elif author:
            cursor.execute(query, (session['user_id'], f"%{author}%"))
        elif category:
            cursor.execute(query, (session['user_id'], f"%{category}%"))
        elif title:
            cursor.execute(query, (session['user_id'], f"%{title}%"))
        else:
            cursor.execute(query, (session['user_id'],))

        books = cursor.fetchall()

        # Get the number of reservations made by the user in the current week
        current_date = datetime.date.today()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        query = """
        SELECT COUNT(*) 
        FROM `transaction`
        WHERE user_id = %s AND date_of_reservation BETWEEN %s AND %s
        """
        cursor.execute(query, (session['user_id'], start_of_week, end_of_week))
        reservation_count = cursor.fetchone()[0]

        cursor.close()

        return render_template('all_books.html', books=books, reservation_count=reservation_count)

    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    try:
        isbn = request.form.get('isbn')
        reservation_action = request.form.get('reservation-action')
        user_id = session['user_id']
        cursor = connection.cursor()
        if reservation_action == 'Cancel Reservation':
            query_increase = """
            UPDATE `book`
            SET num_copies = num_copies + 1
            WHERE ISBN = %s
            """
            cursor.execute(query_increase, (isbn,))
            connection.commit()

            # Cancel the reservation without checking the reservation count
            query = """
            DELETE FROM `transaction`
            WHERE ISBN = %s AND user_id = %s AND transaction_type = 0
            """
            cursor.execute(query, (isbn, user_id))
            connection.commit()
            cursor.close()
            redirect_url = request.referrer or url_for('fetch_all_books', author=request.args.get('author'), category=request.args.get('category'), title=request.args.get('title'))

            return redirect(redirect_url)
            
        if reservation_action == 'Reserve': #elif
            # Check the number of reservations made by the user in the current week
            current_date = datetime.date.today()
            start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)

            # Convert start_of_week and end_of_week to timestamp
            start_of_week_timestamp = datetime.datetime.combine(start_of_week, datetime.datetime.min.time())
            end_of_week_timestamp = datetime.datetime.combine(end_of_week, datetime.datetime.max.time())
            query = """
                SELECT COUNT(*)
                FROM `transaction` 
                WHERE user_id = %s AND date_of_reservation BETWEEN %s AND %s
            """
            cursor.execute(query, (user_id, start_of_week_timestamp, end_of_week_timestamp))
            result = cursor.fetchall()

            # Extract the count value from the result
            reservation_count = result[0][0]

            # Print the count value
            print("Count:", reservation_count)

            # Check if the user has reached the maximum number of reservations per week
            if reservation_count >= 2:
                return "You have reached the maximum number of reservations for this week."

        
            else:
                query_decrease = """
                UPDATE `book`
                SET num_copies = num_copies - 1
                WHERE ISBN = %s AND num_copies > 0
                """
                # AND num_copies > 0 for now
                cursor.execute(query_decrease, (isbn,))
                connection.commit()

                # Check if the update was successful (num_copies > 0)
                if cursor.rowcount == 0:
                    return "No available copies for reservation."
        
                # Get the current timestamp
                current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                query = """
                INSERT INTO `transaction` (date_of_max_return, date_of_borrowing, transaction_status, date_of_reservation, transaction_type, date_of_return, ISBN, user_id)
                VALUES (NULL, NULL, 0, %s, 0, NULL, %s, %s)
                """
    
                cursor.execute(query, (current_timestamp, isbn, user_id))
                connection.commit()
                cursor.close()
                redirect_url = request.referrer or url_for('fetch_all_books', author=request.args.get('author'), category=request.args.get('category'), title=request.args.get('title'))

                return redirect(redirect_url)

    except Exception as e:
        print('Error:', e)
        return Response(status=204)

@app.route('/review_book/<isbn>', methods=['GET'])
def review_book(isbn):
    return render_template('review_book.html', isbn=isbn)

@app.route('/submit_review/<isbn>', methods=['POST'])
def submit_review(isbn):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']
    try:
        with connection.cursor() as cursor:
            # Insert the review into the 'review' table
            sql = "INSERT INTO `review` (ISBN, text_of_review, likert_rating, user_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (isbn, comment, rating, user_id))
            connection.commit()

        # Redirect to the book listing page
        return redirect(url_for('fetch_all_books', author=request.args.get('author'), category=request.args.get('category'), title=request.args.get('title')))

    except Exception as e:
        # Handle any database errors
        return "Error: " + str(e)




@app.route('/list_of_borrowed_books', methods=['GET'])
def list_of_borrowed_books():
    # Get the specific_user_id from the request
    specific_user_id = session['user_id']
    try:
        with connection.cursor() as cursor:
            # Execute the SQL query
            query = """
            SELECT t.ISBN, b.title, b.publisher, b.images
            FROM `transaction` t
            JOIN `book` b ON t.ISBN = b.ISBN
            WHERE t.transaction_type = 1
            -- AND t.transaction_status = 1
            AND t.user_id = %s
            GROUP BY t.ISBN
            """
            cursor.execute(query, (specific_user_id,))

            # Fetch all rows from the result set
            results = cursor.fetchall()
     
            cursor.close()
            return render_template('list_of_borrowed_books.html',results=results)
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/fetch_transactions', methods=['GET'])
def fetch_transactions():
    try:
        user_id = request.args.get('user_id')  # Retrieve the user_id
        cursor = connection.cursor()

        # Construct the base query
        query = """
            SELECT date_of_max_return, date_of_borrowing, date_of_return,
            date_of_reservation, ISBN, user_id, transaction_id, transaction_type, transaction_status
            FROM transaction 
            WHERE `transaction_type` IN (0, 1, 2) 
            """

        # Add conditions to the query based on the provided search criteria
        if user_id:
            query += f" AND user_id = '{user_id}'"
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return render_template('transactions.html', results=results)

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

@app.route('/update_transaction_type', methods=['POST'])
def update_transaction_type():
    try:
        transaction_id = request.form.get('transaction_id')  # Retrieve the transaction_id
        action = request.form.get('action')  # Retrieve the action
        
        cursor = connection.cursor()

        # Get the current transaction_type
        get_type_query = f"SELECT transaction_type FROM transaction WHERE transaction_id = '{transaction_id}'"
        cursor.execute(get_type_query)
        current_type = cursor.fetchone()[0]

        # Update the transaction_type based on the action
        if action == 'borrow' and current_type == 0:
            new_type = 1
        elif action == 'return' and current_type == 1:
            new_type = 2
        elif action == 'cancel borrow' and current_type == 1:
            new_type = 0
        elif action == 'cancel return' and current_type == 2:
            new_type = 1
        else:
            return "Invalid action"

        # Update the transaction_type in the database
        update_query = f"UPDATE transaction SET transaction_type = '{new_type}' WHERE transaction_id = '{transaction_id}'"
        cursor.execute(update_query)
        connection.commit()

        cursor.close()

        return redirect(url_for('fetch_transactions'))

    except Exception as e:
        return f"An error occurred: {str(e)}"



@app.route('/create_borrow', methods=['GET', 'POST'])
def create_borrow():
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id')  # Retrieve the user_id from the form
            isbn = request.form.get('isbn')  # Retrieve the ISBN from the form
            
            # Insert a new borrow transaction into the database
            cursor = connection.cursor()
            insert_query = f"INSERT INTO transaction (transaction_type, user_id, ISBN) VALUES (1, '{user_id}', '{isbn}')"
            cursor.execute(insert_query)
            connection.commit()
            cursor.close()
            
            return redirect(url_for('fetch_transactions'))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    else:
        return render_template('create_borrow.html')
