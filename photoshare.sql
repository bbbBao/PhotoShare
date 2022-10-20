CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
SET GLOBAL sql_mode='';

CREATE TABLE Users(
 user_id INTEGER AUTO_INCREMENT,
 first_name VARCHAR(100),
 last_name VARCHAR(100),
 email VARCHAR(100),
 birth_date DATE,
 hometown VARCHAR(100),
 gender VARCHAR(100),
 password VARCHAR(100) NOT NULL,
 contribution int(11) NOT NULL DEFAULT '0',
 PRIMARY KEY (user_id)
 );

 CREATE TABLE Friends(
 user_id1 INTEGER,
 user_id2 INTEGER,
 PRIMARY KEY (user_id1, user_id2),
 FOREIGN KEY (user_id1)
 REFERENCES Users(user_id),
 FOREIGN KEY (user_id2)
 REFERENCES Users(user_id)
);

CREATE TABLE Albums(
 albums_id INTEGER AUTO_INCREMENT,
 name VARCHAR(100),
 date DATE,
 user_id INTEGER NOT NULL,
 PRIMARY KEY (albums_id),
 FOREIGN KEY (user_id)
 REFERENCES Users(user_id)
);



CREATE TABLE Photos(
 photo_id INTEGER AUTO_INCREMENT,
 caption VARCHAR(100),
 data LONGBLOB,
 albums_id INTEGER,
 user_id INTEGER,
 PRIMARY KEY (photo_id),
 FOREIGN KEY (albums_id) REFERENCES Albums (albums_id) ON DELETE CASCADE,
 FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

CREATE TABLE Tags(
 tag_id INTEGER AUTO_INCREMENT,
 photo_id INTEGER,
 name VARCHAR(100),
 PRIMARY KEY (tag_id),
 FOREIGN KEY (photo_id) REFERENCES Photos (photo_id) ON DELETE CASCADE
 
);

CREATE TABLE Comments(
 comment_id INTEGER AUTO_INCREMENT,
 user_id INTEGER NOT NULL,
 photo_id INTEGER NOT NULL,
 text VARCHAR (100),
 date DATE,
 PRIMARY KEY (comment_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id)
);

CREATE TABLE Likes(
 photo_id INTEGER,
 user_id INTEGER,
 PRIMARY KEY (photo_id,user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id)
);

INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('tianyib@bu.edu', 'bao', 'Tianyi', 'Bao', 'Shanghai', 'Male', '2000-08-31', '10');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('tomh@bu.edu', 'tom', 'Tom', 'Holland', 'London', 'Male', '1995-02-11', '6');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('stevej@apple.com', 's_jobs', 'Steve', 'Jobs', 'Palo Alto', 'Male', '1955-02-24', '7');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('sammy@cat.com', 'sammy_fish', 'Sammy', 'Cat', 'Boston', 'Female', '2020-04-19', '10');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('albert@bu.edu', 'test', 'Alberto', 'Handley', 'Tokyo', 'Female', '1999-03-12', '0');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('rumaisa@bu.edu', 'test', 'Rumaisa', 'Cote', 'Beijing', 'Male', '1989-04-04', '2');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('daniekius@bu.edu', 'test', 'Danielius', 'Vazquez', 'New York', 'Male', '2000-07-10', '9');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('margie@bu.edu', 'test', 'Margie', 'Palacios', 'Los Angeles', 'Female', '1993-11-20', '3');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('casper@bu.edu', 'test', 'Casper', 'Draper', 'Arlington', 'Male', '1988-01-02', '8');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('nyle@bu.edu', 'test', 'Nyle', 'Austin', 'San Francisco', 'Male', '2001-10-17', '6');
INSERT INTO Users (email, password, first_name, last_name, hometown, gender, birth_date, contribution) VALUES ('nasir@bu.edu', 'test', 'Nasir', 'Humphreys', 'Frankfurt', 'Female', '1992-09-22', '5');

