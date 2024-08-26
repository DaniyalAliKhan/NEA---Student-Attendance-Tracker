#We begin with the improting of all the necessary libraries needed for our program
import sqlite3
from datetime import datetime
import tkinter as tk
import ttkbootstrap as ttk
import hashlib
from datetime import timedelta
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import os
import tkinter.font as font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from datetime import date as dt_date
from collections import deque
#The line below retirves the connect_to_database function from our database.py file
from database import connect_to_database



#Creation of the classes that will be utilised throughout the program
class teacher():
    def __init__(self,emailid,name,role,subject,assigned,leading):
        self.emailid = emailid
        self.name = name
        self.role = role
        self.subject = subject
        self.assigned = assigned
        self.leading = leading
    
    def timetableread(self, current_day):
        teacher_timetable = []
        table_column_name = current_day + 'Timetable'
        cursor.execute(f"SELECT {table_column_name} FROM Teacher WHERE Teacheremail = ?", (self.emailid,))
        timetable = cursor.fetchall()
        timetable = timetable[0][0]
        #Timetables for teachers are stored with the year group associated with them for each lesson so we have retirved both the teacher timetable and timetable in terms of which years they are teaching
        teacher_timetable = [None if entry == 'Free' else entry.split('-')[0] for entry in timetable.split(',')]
        year_timetable = [None if entry == 'Free' else entry.split('-')[1] for entry in timetable.split(',')]
        return teacher_timetable,year_timetable

    def Get_Students_For_Teacher(self,Student_List,lesson_start_times):
        #This subroutine will retrieve through relating the information stored about teachers in the database with the information about students stored in the database
        current_lesson = None
        subject = self.subject
        year_group_assigned = self.assigned
        year_group_assigned = [number for number in year_group_assigned.split(',')]
        matching_students = []
        current_time_string = datetime.now().strftime('%H:%M')
        current_datetime = datetime.strptime(current_time_string, '%H:%M')
        #The Loop below identifies the current lesson of the teacher
        for i in range(len(lesson_start_times) - 1):
            lesson_start_time = datetime.strptime(lesson_start_times[i], '%H:%M')
            if lesson_start_time <= current_datetime < datetime.strptime(lesson_start_times[i + 1], '%H:%M'):
                current_lesson = i   
                break
        if current_lesson is not None:
            current_date = datetime.now()
            current_day = current_date.strftime("%A")
            teacher_timetable, year_timetable = self.timetableread(current_day)
            teacher_lesson = teacher_timetable[i]
            for student_id, student in Student_List.items():
                #The code now retirves the students who are part of the teacher's lessons by linking the subjects and year groups 
                if subject in student.subjects.split(',') and student.year in year_group_assigned:
                    student_timetable = student.get_timetable_for_day(student.id,current_day)
                    #It checks if the student has the same lesson as the teacher at that time and if they do they are addedd to the matching students list
                    if len(student_timetable) > 0 and student_timetable[int(current_lesson)] == teacher_lesson:
                        matching_students.append(student)
        else:
            matching_students = []
        return(matching_students,current_lesson)

    def subject_specific_student_analysis(self):
        if AnalysisStudentChoice.get() == '':
            input_error()
        else:
            try:
                StatsFrame.forget()
            except:
                pass
            #The SQL query below retirevs all the students records associated with that particular teacher and implements them as a graph
            cursor.execute('''
                SELECT Lateness
                FROM Attendance
                WHERE Studentemail = ? AND Teacheremail = ?
                ''', (AnalysisStudentChoice.get().strip(),self.emailid,))
            attendance_records = cursor.fetchall()
            if attendance_records != []:
                posx = ['0','1','2','3','4','5 beyond','Absent']
                posy = [0,0,0,0,0,0,0]
                for i in range (len(attendance_records[0])):
                    if attendance_records[0][i] == 0:
                        posy[0] += 1
                    if attendance_records[0][i] == 1:
                        posy[1] += 1
                    if attendance_records[0][i] == 2:
                        posy[2] += 1
                    if attendance_records[0][i] == 3:
                        posy[3] += 1
                    if attendance_records[0][i] == 4:
                        posy[4] += 1
                    if attendance_records[0][i]  >= 5 and attendance_records[0][i] < 99:
                        posy[5] += 1
                    if attendance_records[0][i] == 99:
                        posy[6] += 1
                AnalysisStudentChoice.delete(0, tk.END)
                plt.bar(posx, posy)
                plt.xlabel('Lateness (minutes)')
                plt.ylabel('Frequnecy')
                plt.title('Lateness Distribution for Lesson')
                plt.show()
            else:
                NoRecords = tk.Tk()
                NoRecords.title('No Record Found')
                NoRecordLabel = ttk.Label(master=NoRecords, text='No records have been found for the studnet entered')
                ok_button = tk.Button(master=NoRecords, text="OK", command=NoRecords.destroy)
                NoRecordLabel.pack()
                ok_button.pack()
    
    
        

    

class Head_of_Year(teacher):
    #The Head of Year class is a subclass of Teacher
    def __init__(self, emailid, name, role, subject, assigned,leading):
        super().__init__(emailid, name, role, subject, assigned,leading)

    def subject_specific_student_analysis(self):
        #Here polymorphism occurs as the teacher class has a similar analysis but Head of Years can carry out with any teahcer in their year group
        if AnalysisStudentChoice.get() == '' or Specific_Analysis_Email_Entry.get() == '':
            input_error()
        else:
            try:
                StatsFrame.forget()
            except:
                pass
            cursor.execute('''
                SELECT Lateness
                FROM Attendance
                WHERE Studentemail = ? AND Teacheremail = ?
                ''', (AnalysisStudentChoice.get().strip(), Specific_Analysis_Email_Entry.get().strip(),))
            attendance_records = cursor.fetchall()
            if attendance_records != []:
                posx = ['0','1','2','3','4','5 beyond','Absent']
                posy = [0,0,0,0,0,0,0]
                for i in range (len(attendance_records[0])):
                    if attendance_records[0][i] == 0:
                        posy[0] += 1
                    if attendance_records[0][i] == 1:
                        posy[1] += 1
                    if attendance_records[0][i] == 2:
                        posy[2] += 1
                    if attendance_records[0][i] == 3:
                        posy[3] += 1
                    if attendance_records[0][i] == 4:
                        posy[4] += 1
                    if attendance_records[0][i] >= 5 and attendance_records[0][i] < 99:
                        posy[5] += 1
                    if attendance_records[0][i] == 99:
                        posy[6] += 1
                AnalysisStudentChoice.delete(0, tk.END)
                plt.bar(posx, posy)
                plt.xlabel('Lateness (minutes)')
                plt.ylabel('Frequency')
                plt.title('Lateness Distribution for Lesson')
                plt.show()
            else:
                NoRecords = tk.Tk()
                NoRecords.title('No Record Found')
                NoRecordLabel = ttk.Label(master=NoRecords, text='No records have been found for the studnet entered')
                ok_button = tk.Button(master=NoRecords, text="OK", command=NoRecords.destroy)
                NoRecordLabel.pack()
                ok_button.pack()
    
    #Further Analysis are shown below that the Head of Year will have access to 
    def WeekAnalysis(self):
        student_list = []
        start_date_str = Startcalendar.entry.get()
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y')

        end_date_str = Endcalendar.entry.get()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y')

        all_dates = [start_date]

        while start_date < end_date:
            start_date += timedelta(days=1)
            all_dates.append(start_date)

        for i in range(len(all_dates)):
            date_string = all_dates[i].strftime("%Y-%m-%d")
            year_list = self.leading.split(',')
            for year in year_list:
                cursor.execute('''
                    SELECT A.* FROM Attendance A
                    INNER JOIN Student S ON A.Studentemail = S.Studentid
                    WHERE A.LessonID LIKE ? AND S.year = ?
                ''', (f"{date_string}%", year,))
                # An inner join is carried out between the two tables in order to retirve all the necessary records for the weeks inputted for the Year Groups the Head of Year is assigned
                records = cursor.fetchall()
                student_list.extend(records)

        if student_list != []:
            posx = ['0', '1', '2', '3', '4', '5 beyond', 'Absent']
            posy = [0, 0, 0, 0, 0, 0, 0]

            for i in range(len(student_list)):
                lateness = student_list[i][6]
                if lateness == 0:
                    posy[0] += 1
                elif lateness == 1:
                    posy[1] += 1
                elif lateness == 2:
                    posy[2] += 1
                elif lateness == 3:
                    posy[3] += 1
                elif lateness == 4:
                    posy[4] += 1
                elif lateness == 99:
                    posy[6] += 1
                else:
                    posy[5] += 1

            plt.bar(posx, posy)
            plt.xlabel('Lateness (minutes)')
            plt.ylabel('Number of Students')
            plt.title('Lateness Distribution for Week')
            plt.show()
        else:
            NoRecords = tk.Tk()
            NoRecords.title('No Record Found')
            NoRecordLabel = ttk.Label(master=NoRecords, text='No records have been found for the week entered')
            ok_button = tk.Button(master=NoRecords, text="OK", command=NoRecords.destroy)
            NoRecordLabel.pack()
            ok_button.pack()

    def student_analysis(self):
        IdCode = HOY_Student_Code.get().strip()
        if IdCode == '':
            input_error()
        else:
            HOY_Student_Code.delete(0, tk.END)
            attendance_records = []
            cursor.execute('''
            SELECT
                COUNT(CASE WHEN Lateness = 0 THEN 1 END) AS PresentStudents,
                COUNT(CASE WHEN Lateness = 1 THEN 1 END) AS Late1,
                COUNT(CASE WHEN Lateness = 2 THEN 1 END) AS Late2,
                COUNT(CASE WHEN Lateness = 3 THEN 1 END) AS Late3,
                COUNT(CASE WHEN Lateness = 4 THEN 1 END) AS Late4,
                COUNT(CASE WHEN Lateness >= 5 AND Lateness < 99 THEN 1 END) AS Late5Plus,
                COUNT(CASE WHEN Lateness = 99 THEN 1 END) AS AbsentStudents
            FROM Attendance
            WHERE StudentEmail = ?
            ''', (IdCode,))
            #Here aggregate SQL functions have been implemented in order to efficiently retrieve the neccessary lateness records from the database
            attendance_records = cursor.fetchall()
            if attendance_records != [(0,0,0,0,0,0,0)]:
                posx = ['0','1','2','3','4','5 beyond','Absent']
                posy = [0,0,0,0,0,0,0]
                posy[0] = attendance_records[0][0]
                posy[1] = attendance_records[0][1]
                posy[2] = attendance_records[0][2]
                posy[3] = attendance_records[0][3]
                posy[4] = attendance_records[0][4]
                posy[5] = attendance_records[0][5]
                posy[6] = attendance_records[0][6]
                plt.bar(posx, posy)
                plt.xlabel('Lateness (minutes)')
                plt.ylabel('Frequency')
                plt.title('Lateness Distribution for Student')
                plt.show()
            else:
                NoRecords = tk.Tk()
                NoRecords.title('No Record Found')
                NoRecordLabel = ttk.Label(master=NoRecords, text='No records have been found for the studnet entered')
                ok_button = tk.Button(master=NoRecords, text="OK", command=NoRecords.destroy)
                NoRecordLabel.pack()
                ok_button.pack()
            
    def congregation_analysis(self):
        class_names = []
        result = []
        year_list = self.leading.split(',')
        for year in year_list:
            cursor.execute('''
                SELECT SWIPE.Class_Name
                FROM SWIPE
                INNER JOIN Student ON SWIPE.Studentid = Student.Studentid
                WHERE SWIPE.Block = 'Y' AND Student.year = ?
            ''', (year,))
            #Checks against the enteries in the Swipe Table for the amount of classrooms blocked
            search = cursor.fetchall()
            if search != []: 
                result.extend(search)
        if result != []:
            #Here a dictionary is created where it takes all the different classes where there is a Swipe Block and checks the frequency of apperance of each
            class_name_counts = {}  
            for row in result:
                class_name = row[0]
                if class_name in class_name_counts:
                    class_name_counts[class_name] += 1
                else:
                    class_name_counts[class_name] = 1
            class_names = list(class_name_counts.keys())
            counts = list(class_name_counts.values())
            plt.bar(class_names, counts)
            plt.xlabel('Class Name')
            plt.ylabel('Frequency')
            plt.title('Class Name Frequency with Block = Y')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
        else:
            NoRecord = tk.Tk()
            WarningMessage = ttk.Label(master=NoRecord, text = 'No records have been found')
            ok_button = tk.Button(NoRecord, text="OK", command=NoRecord.destroy)
            WarningMessage.pack()
            ok_button.pack()



    def subject_analysis(self):
        Subject = SubjectAnalysis_Entry.get().strip()
        if Subject == '':
            input_error()
        else:
            SubjectAnalysis_Entry.delete(0, tk.END)
            emails = []
            attendance_records = []
             #Here it retrieves all the teacher's emails who are teaching a particular subject so they can be further used in a search
            cursor.execute('''
            SELECT Teacheremail
            FROM Teacher
            WHERE Subject = ?
            ''', (Subject,))
            emails = cursor.fetchall()
            year_list = self.leading.split(',')
            for i in range(len(emails)):
                email = emails[i][0]
                #The code below then finds the students linked with the attendance records that are stored for those teachers and checks if the student is in the same year group assigned to the head of year before retriving any values
                for year in year_list:
                    cursor.execute('''
                        SELECT A.* FROM Attendance A
                        INNER JOIN Student S ON A.Studentemail = S.Studentid
                        WHERE A.LessonID LIKE ? AND S.year = ? 
                        ''', (f"%-{email}-%", year))
                    records = cursor.fetchall()
                    attendance_records.extend(records)
            if attendance_records != []:
                posx = ['0', '1', '2', '3', '4', '5 beyond', 'Absent']
                posy = [0, 0, 0, 0, 0, 0, 0]
                for i in range(len(attendance_records)):
                    lateness = attendance_records[i][6]
                    if lateness == 0:
                        posy[0] += 1
                    elif lateness == 1:
                        posy[1] += 1
                    elif lateness == 2:
                        posy[2] += 1
                    elif lateness == 3:
                        posy[3] += 1
                    elif lateness == 4:
                        posy[4] += 1
                    elif lateness == 99:
                        posy[6] += 1
                    else:
                        posy[5] += 1

                plt.bar(posx, posy)
                plt.xlabel('Lateness (minutes)')
                plt.ylabel('Number of Students')
                plt.title('Lateness Distribution for Lesson')
                plt.show()
            else:
                NoRecords = tk.Tk()
                NoRecords.title('No Record Found')
                NoRecordLabel = ttk.Label(master=NoRecords, text='No records have been found for the subject entered')
                ok_button = tk.Button(master=NoRecords, text="OK", command=NoRecords.destroy)
                NoRecordLabel.pack()
                ok_button.pack()
    

class Student():
    def __init__(self, id, forename, surname, year, subjects):
        self.id = id
        self.forename = forename
        self.surname = surname
        self.year = year
        self.subjects = subjects

    def get_timetable_for_day(self,id,current_day):
        column_name = f'{current_day}Timetable'
        # Retrieve the timetable for the student from the database
        cursor.execute(f"SELECT {column_name} FROM Student WHERE Studentid = ?", (self.id,))
        result = cursor.fetchone()
        if result:
            timetable_string = result[0]  
            timetable_list = timetable_string.split(',')
        return timetable_list

    #Here it gets the student's leaving records for their previous lesson. Note that Swipe Direction 0 means leaving the room and 1 will refer to entry
    def Get_Last_Lesson_Leave(self,current_lesson):
        result = []
        current_date = datetime.now()
        current_day = current_date.strftime("%A")
        current_date_search = str(datetime.now().date())
        timetable = self.get_timetable_for_day(self.id,current_day)
        #Certian lessons do not have a direct fetching ability so we must take them into account
        if current_day != 'Friday':
            Restricted_Lessons = [0,3,6]
        else:
            Restricted_Lessons = [0,3]
        #Now the statements below take account of 3 different scenarios. 
        if current_lesson not in Restricted_Lessons:
            last_lesson = timetable[current_lesson - 1]
            #Here it checks if the last_lesson is free then it checks for Students having left the terrace and common room and making sure that time is before the start time of the current lesson
            if last_lesson == 'Free':
                cursor.execute('''
                        SELECT SwipeID, SwipeDirection, Class_Name, Time,ClassID,Studentid
                        FROM SWIPE
                        WHERE Class_Name = 'Terrace' or Class_Name = 'Common Room' AND Studentid = ? AND SwipeDirection = 0 AND Date = ?
                        ORDER BY Time DESC
                        LIMIT 1       ''', ( self.id, current_date_search))
                result = cursor.fetchone()
            #If the student has a proper lesson before a simple fetch is carried out 
            else:
                cursor.execute('''
                        SELECT SwipeID, SwipeDirection, Class_Name, Time,ClassID,Studentid
                        FROM SWIPE
                        WHERE Class_Name = ? AND Studentid = ? AND SwipeDirection = 0 AND Date = ?
                        ORDER BY Time DESC
                        LIMIT 1       ''', (last_lesson, self.id, current_date_search))
                result = cursor.fetchone()
        #The system then checks if the lesson is the first lesson and since there is no lesson before the first it instead checks if the student has signed out of their form rooms where records will simply be stored with class name as Form
        elif current_lesson == 0:
            cursor.execute('''
                        SELECT SwipeID, SwipeDirection, Class_Name, Time,ClassID,Studentid
                        FROM SWIPE
                        WHERE Class_Name = 'Form' AND Studentid = ? AND SwipeDirection = 0 AND Date = ?
                        ORDER BY Time DESC
                        LIMIT 1   ''', (self.id, current_date_search))
            result = cursor.fetchone()
        #If the students had break before the current lesson the system checks for them in 3 potential location they may be in to get their leaving time and once again makes sure it is leaving time for the current class 
        else:
            cursor.execute('''
                SELECT SwipeID, Class_Name, Time
                FROM SWIPE
                WHERE Studentid = ? AND Class_Name IN ('Canteen', 'Terrace', 'Common Room') AND SwipeDirection = 0 AND Date = ?
                ORDER BY Time DESC
                LIMIT 1''', (self.id, current_date_search))
            result = cursor.fetchone()
        return(result)
    
    def get_current_lesson_join(self,current_lesson):
        #There is now a method to pair with the previous one to check if the student has arrived to the current ongoing lesson
        result = []
        current_date = datetime.now()
        current_day = current_date.strftime("%A")
        current_date_search = str(datetime.now().date())
        timetable = self.get_timetable_for_day(self.id,current_day)
        joining_lesson = timetable[current_lesson]
        cursor.execute('''
                       SELECT SwipeID, SwipeDirection, Class_Name, Time,ClassID,Studentid
                       FROM SWIPE
                       WHERE Class_Name = ? AND Studentid = ? AND SwipeDirection = 1 AND Date = ?''', (joining_lesson, self.id, current_date_search))
        result = cursor.fetchone()
        return(result)
    
    def Day_Attendance_Display(self):
        #This methods will display all the attendance records for a Student in a singular day
        date_string = datetime.now().strftime('%Y-%m-%d')
        #The system retrieves all the final Attendance so Present, Late, Absent for each lesson
        cursor.execute('''
                    SELECT Attendance FROM Attendance 
                    WHERE LessonID LIKE ? AND Studentemail = ?
                ''', (f"{date_string}%", self.id,))

        results = cursor.fetchall()
        
        if results:
            attendance_window = tk.Tk()
            attendance_window.title("Day Attendance Display")
        #The records are put into a table and then displayed with different colors for each attendace type 
            columns = ['Student Per Lesson Attendance']
            colors = {'A': 'lightcoral', 'P': 'lightgreen', 'L': 'lightyellow'}

            tree = ttk.Treeview(attendance_window, columns=columns, show='headings', style='Custom.Treeview')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100) 
            #The system the inputs the records and configures the rows accordingly
            try:
                for row in results:
                    values = row[0].split(',') if row[0] else [''] * len(columns)
                    item_id = tree.insert("", "end", values=values)

                    for col, status in enumerate(values):
                        tag_name = f"{col}_{status}"
                        tree.tag_configure(tag_name, background=colors.get(status, 'white'))
                        tree.item(item_id, values=([''] * col) + [status] + ([''] * (len(columns) - col - 1)), tags=(tag_name,))
            except:
                pass

            tree.pack(fill='both', expand=True)
    
        else:
            NoRecord = tk.Tk()
            WarningMessage = ttk.Label(master=NoRecord, text='No records stored for the student for the day')
            ok_button = tk.Button(NoRecord, text="OK", command=NoRecord.destroy)
            WarningMessage.pack()
            ok_button.pack()

                    

    
class Node:
    def __init__(self, data, weight):
        self.data = data
        self.weight = weight
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_node(self, data, weight):
        new_node = Node(data, weight)
        if not self.head:
            self.head = new_node
        else:
            current_node = self.head
            while current_node.next:
                current_node = current_node.next
            current_node.next = new_node

class Graph:
    def __init__(self):
        self.graph = {}

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = LinkedList()

    def add_edge(self, node1, node2, weight):
        if node1 not in self.graph:
            self.graph[node1] = LinkedList()
        if node2 not in self.graph:
            self.graph[node2] = LinkedList()
    # As Students are not restricted in walking from one class to another in whichever direction they want the nodes in the graph have to be added in a bidrectional manner to ensure we have an accurate graph for the school
        self.graph[node1].add_node(node2, weight)
        self.graph[node2].add_node(node1, weight)
    
    def shortest_path(self, start, end):
        #Here is the implementation of the Shortest Path algorithim using a double-ended queue
        distances = {node: float('inf') for node in self.graph}
        previous_nodes = {}
        distances[start] = 0
        queue = deque([(0, start)])

        while queue:
            current_distance, current_node = queue.popleft()

            if current_node == end:
                path = []
                while current_node:
                    path.insert(0, current_node)
                    current_node = previous_nodes.get(current_node)
                return distances[end]

            if current_node not in self.graph:
                continue

            current_linked_list = self.graph[current_node]

            current_linked_node = current_linked_list.head
            while current_linked_node:
                neighbor, weight = current_linked_node.data, current_linked_node.weight
                potential_distance = distances[current_node] + weight

                if potential_distance < distances[neighbor]:
                    distances[neighbor] = potential_distance
                    previous_nodes[neighbor] = current_node
                    queue.append((distances[neighbor], neighbor))

                current_linked_node = current_linked_node.next

        return float('inf')
    
    def Estimated_Arrival_Time(self,Student_Swipe_Records,end_node):
        #The estimated arrival time is used to trigger the shortets path function 
        start_node = Student_Swipe_Records[4]
        shortest_distance = self.shortest_path(start_node, end_node)
        return shortest_distance
    
    
    def time_dependent_ids(self, start_node, target_time):
        #Here is the implementation for the iterative deepening search
        max_depth = 5
        potential_nodes = set()
        target_time = int(target_time)
        for depth_limit in range(1, max_depth + 1):
            stack = [(start_node, 0, {start_node})]  
            while stack:
                node, current_time, visited_nodes = stack.pop()
                
                if current_time > target_time:
                    continue
                
                if current_time == target_time:
                    if node not in potential_nodes:
                        potential_nodes.add(node)
                    continue 
                
                if len(visited_nodes) < len(self.graph):
                    if node in self.graph:
                        current_linked_list = self.graph[node]
                        current_linked_node = current_linked_list.head

                        while current_linked_node:
                            neighbor, edge_time = current_linked_node.data, current_linked_node.weight
                            new_time = current_time + edge_time

                            if neighbor not in visited_nodes:
                                stack.append((neighbor, new_time, visited_nodes.union({neighbor})))
                            current_linked_node = current_linked_node.next
        return list(potential_nodes)

    

            

def Hashing(password):
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the encoded password
    sha256.update(password.encode('utf-8'))
    # Get the hexadecimal representation of the hashed password
    hashed_password = sha256.hexdigest()

    # Return the hashed password
    return hashed_password

def merge_sort_treeview(treeview, column_index):
    
    def merge_sort(data):
        #It checks if data needs to be sorted if it is more than one item
        if len(data) <= 1:
            return data
        
        #The mid point of the data list is identified and the list split in half
        mid = len(data) // 2
        left_half = data[:mid]
        right_half = data[mid:]
        #The merge sort function is then carried out on each half
        left_half = merge_sort(left_half)
        right_half = merge_sort(right_half)

        return merge(left_half, right_half)

    def merge(left, right):
        #The system is initalised to begin merging the list 
        result = []
        i = j = 0
        #It checks if the values of i and j are less than the values in the list as that will tell us if all the values are sorted in the final list
        while i < len(left) and j < len(right):
            #Compares the values on each side and adds in the smaller one
            if left[i][column_index] < right[j][column_index]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        # Append any remaining elements from both halves
        result.extend(left[i:])
        result.extend(right[j:])

        return result
    
    current_data = [treeview.item(item, 'values') for item in treeview.get_children()]
    sorted_data = merge_sort(current_data)
     
    # Clears the Treeview
    treeview.delete(*treeview.get_children())
    
    # Insert the sorted data back into the Treeview
    for item in sorted_data:
        treeview.insert('', 'end', values=item)


#The graph object is created with all the nodes and edges in a list 
graph = Graph()

nodes = ['SF054', 'T1', 'SF053', 'SF055', 'SF052', 'SF051', 'E6', 
         'SF048', 'SF044', 'SF047', 'SF043', 'E4', 'TR1', 'TR2', 
         'SF012', 'E3', 'SF011', 'SF013', 'SF014', 'SF010', 'SF015', 'SF009', 
         'T2', 'SF018', 'SF017', 'SF008', 'SF007', 'SF006', 'SF026', 'SF005', 
         'E1', 'SF004', 'SF003', 'SF002', 'SF034', 'SF001', 'FF061', 'P1', 'C1', 
         'L1', 'P2', 'FF014', 'FF013', 'FF012', 'FF011', 
         'FF010', 'FF009', 'FF008', 'FF004', 'FF007', 'FF001','FF005','C2','T3',
         'SF041']

edges = [('SF054', 'T1', 10), ('SF054', 'SF053', 7), ('SF054', 'SF055', 6), ('SF053', 'T1', 8),
         ('SF053', 'SF055', 7), ('SF052', 'SF055', 10), ('SF052', 'SF051', 7), ('SF052', 'E6', 7),
         ('SF051', 'E6', 5), ('SF051', 'SF048', 10), ('SF051', 'SF044', 10), ('SF048', 'SF044', 5),
         ('SF048', 'E6', 12), ('SF048', 'SF047', 6), ('SF047', 'SF043', 5), ('SF047', 'SF044', 7),
         ('SF043', 'SF044', 9), ('SF044', 'E6', 8), ('E6', 'SF055', 10), ('SF055', 'T1', 10),   
         ('SF053','SF052',7),('SF042','SF043',15),('SF042','SF041',10),('SF041','SF040',10),('SF041','E4',10),   
         ('TR1','E4',6), ('TR2','TR1',10),('TR2','SF012',10), ('TR2','E3',15), ('SF012','E3',6),('SF012','SF011',10),   
         ('E3','SF011',7), ('E3','SF013',8),('SF013','SF012',7),('SF013','SF014',7),('SF011','SF013',6),('SF013', 'SF010', 8),
         ('SF011','SF014',8),('SF011','SF010',6), ('SF014','SF010',6),('SF014','SF015',9),('SF014','SF009',10),('SF010','SF015',10),  
         ('SF010','SF009',7), ('SF015','SF009', 8), ('SF015','T2',10), ('SF015','SF018',12), ('SF009','T2',10),('T2','SF018',7),  
         ('SF018','SF017',10), ('SF018','SF008',8), ('T2','SF008',9), ('SF008','SF007',6),('SF007','SF006',6),('SF026','SF006',7),
         ('SF006','SF005',6), ('SF026','SF005',7), ('SF026','E1', 15),('SF005','SF004',6),('SF003','SF004',5), ('SF003','E1',9),
         ('SF003','SF002',7),('E1','SF002',9), ('E1','SF034',8),('SF001','SF002',7),('SF002','SF034',6),('SF034','SF001',8),('E4','L1',6),('E4','FF061',8),
         ('E4','P1',6), ('E4','C1',9),('L1','FF061',9), ('L1','P1',5), ('L1','P2',10),('P2','P1',7), ('FF061','P1',8),('FF061','C1',13),
         ('C1','C2',10), ('C2','E3',10),('E3','T3',20), ('T3','FF014',12),('T3','FF013',9),('FF013','FF012',6),('FF011','FF012',6),
         ('FF011','FF010',6), ('FF010','FF009',6), ('FF009','FF008',8) ,('FF008','E1',8), ('FF008','FF004',10), ('E1','FF004',14), 
         ('E1','FF007',15),('FF004','FF007',9),('FF004','FF001',6), ('FF001','FF005',5),('FF005','FF007',7) ]


#The graph methods are used to add nodes and add edges into the system 
for node in nodes:
    graph.add_node(node)

for edge in edges:
    graph.add_edge(edge[0], edge[1], edge[2])

#The system then conencts to the database through the imported function
connection, cursor = connect_to_database()

Student_List = {}
#It now retrieves all the records for students in the student table and then start to create objects for all the students in order for the class functions associated with them to be utilsied
cursor.execute('SELECT Studentid, forename, surname, year, subjects FROM Student')
rows = cursor.fetchall()
for row in rows:
    studentid, forename, surname, year, subjects = row
    student = Student(studentid, forename, surname, year, subjects)
    Student_List[studentid] = student

#This links the class to their RFID ID, Teahcer, Subject and Class ID 
Class_RFID_Dictionary = {'SF054': {'ClassName': 'Math', 'Teacher':'J.Smith' ,'RFIDID': '00032'},
                         'SF053': {"ClassName": 'Computer Science', 'Teacher':'Unknown' ,'RFIDID': '053'},
                         'SF051': {'ClassName': 'Physics', 'Teacher':'K.King' ,'RFIDID': '051'},
                         'SF055': {'ClassName': 'Business', 'Teacher':'K.King','RFIDID': '055'},
                         'SF042': {'ClassName': 'Drama', 'Teacher': 'Teacher','RFIDID': '042'}
                         }







def signup(email,forename,surname,Password,subject,yearassigned,role,Monday,Tuesday,Wednesday,Thursday,Friday,RoomID,Leading):
    Approved = False
    #The code carries out the hashing algorithim in order to keep the teacher's passwords safe
    Password = Hashing(Password)
    #A connection is established to the database
    connection = sqlite3.connect('Student_Attendance_Management_System.db')
    cursor = connection.cursor()
    #The RFID_ID which is the the room number the teacher will use is taken from the Sign Up enteries
    #A record is inserted into the Teacher table and then saved
    cursor.execute('''INSERT INTO Teacher VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(email,forename,surname,Password,yearassigned,subject,role,Leading,Monday,Tuesday,Wednesday,Thursday,Friday,RoomID))
    connection.commit() 
    Approved = True  
    return(Approved)             

def login(email,Password):
    #The hashed password is obtained
    Password = Hashing(Password)
    #A connection is established with the database
    with sqlite3.connect('Student_Attendance_Management_System.db') as connection:
        cursor = connection.cursor()
    #The SQl statement means that the table is searched for a record matching the email the teacher used to Log In
    cursor.execute('''
    SELECT Teacheremail,Password
    FROM Teacher
    WHERE Teacheremail = ?
    ''', (email,))
    Checking_Database = cursor.fetchone()
    #If no records are retrieved meaning there is no entry for that email in the table of the email, password don't match the ones entered then the program doesn't accept it as a valid login if they do the login is valid
    if Checking_Database != None and Checking_Database[0] == email and  Checking_Database[1] == Password :
        Sucessful = True
    else:
        Sucessful = False
        LoginFailed = tk.Tk()
        LoginFailed.title('LogIn Failed')
        WarningMessage = ttk.Label(master=LoginFailed, text = 'Incorrect Email or Password Entry!')
        ok_button = tk.Button(LoginFailed, text="OK", command=LoginFailed.destroy)
        WarningMessage.pack()
        ok_button.pack(pady=10)
    return Sucessful
    



def updatepassword(email,newpassword):
    #Checks if new Password actually has a some data in it 
    if newpassword == '':
        input_error()
    #Updates the Teacher table with the new password for that record 
    else:
        newpassword = Hashing(newpassword)
        cursor.execute('''
                UPDATE Teacher
                SET Password = ?
                WHERE Teacheremail = ?
            ''', (newpassword,email))
        connection.commit()
        NewPasswordEntry.delete(0, tk.END)
        NewPasswordLabel.grid_forget()
        NewPasswordEntry.grid_forget()
        NewPasswordSumbit.grid_forget()
        InitalPasswordEntry.delete(0, tk.END)



def get_class_key_by_teacher(teacher_name):
    #Gets the RoomID from the Teacher record stored in the database
    cursor.execute('''
    SELECT RoomID
    FROM Teacher
    WHERE TeacherEmail = ? 
                   ''',(teacher_name,))
    end_node = cursor.fetchall()
    return(end_node)
    






def FindingSystem(studentid):
    #The system checks for the latest swipe records for a student and then attempts to retrieve this record
    Status = ''
    cursor.execute('''
        SELECT *
        FROM SWIPE
        WHERE Studentid = ?
        ORDER BY SwipeID DESC
        LIMIT 1
    ''', (studentid,))
    #It checks if the last swipe was the one that was blocked then assigns Status to Attempted to Enter
    latest_swipe_record = cursor.fetchone()
    if latest_swipe_record != None:
        if latest_swipe_record[5] == 'Y':
            Status = 'Attempted to Enter'
        #If the last swipe was not blocked it checks whether the Swipe Direction was 1 for entered or 0 for leaving a class 
        elif latest_swipe_record[1] == '1':
            Status = 'Entered'
        else:
            Status = 'Left'
    else:
        latest_swipe_record = 'None'
    return (Status,latest_swipe_record)
    



#Below is the Beginning of the code for the Tkinter Application

def input_error():
    #This function basically acts as an input error for the user when in the entries they have put no values in the entry and pres submit
    InputError = tk.Tk()
    InputError.title('No Value Entered')
    InputErrorLabel = ttk.Label(master=InputError, text='Nothing has been put inside the entry!')
    ok_button = tk.Button(InputError, text="OK", command=InputError.destroy)
    InputErrorLabel.pack()
    ok_button.pack()



def beginsignup():
    #All whitespaces in the entries are removed so that not uneccessary characters are stored 
    Email = EmailsignupEntry.get().strip()
    full_name = nameEntry.get().strip()
    forename, _, surname = full_name.partition(' ')
    Password = SignUpPasswordEntry.get().strip()
    Subject = SubjectsBox.get().strip()
    Yeargroup = ''
    #Checks if the Email entered ends with @ascsdubai.ae as all teacher emails end in the value
    if Email.endswith('@alsalamcommunity.ae'):
    #Checks the tkinter CheckBox widgets to get whcih year groups the teacher teaches 
        if Year12.get() == 1:
            Yeargroup += '12'
        if Year13.get() == 1:
            if Yeargroup != '':
                Yeargroup += ', '
            Yeargroup += '13'
        if Year10.get() == 1:
            if Yeargroup != '':
                Yeargroup += ', '
            Yeargroup += '10'
        if Year11.get() == 1:
            if Yeargroup != '':
                Yeargroup += ', '
            Yeargroup += '11'
        #Gets if the teacher is a Head of Year or just a standard teacher
        Role = RoleAssigned.get()
        if Role == 1:
            Role_Assigned ='Teacher'
            Leading = 'None'
        elif Role == 2:
            Role_Assigned = 'Head of Year'
            Leading = LeadingEntry.get().strip()
        #All other neccessary enteries are retrieved 
        RoomID = RoomEntry.get()
        Monday = MondayEntry.get().strip()
        Tuesday = TeusdayEntry.get().strip()
        Wednesday = WednesdayEntry.get().strip()
        Thursday = ThursdayEntry.get().strip()
        Friday = FridayEntry.get().strip()
        #It checks if any of the entries are empty and if they are triggers a Sign Up failed function
        if Email == '' or forename == '' or surname == '' or Password == '' or Monday == '' or Tuesday == '' or Wednesday == '' or Thursday == '' or Friday == '' or RoomID == '':
            SignupFailed = tk.Tk()
            SignupFailed.title('Sign Up Failed')
            WarningMessage = ttk.Label(master=SignupFailed, text = 'You have not filled all the entries!')
            ok_button = tk.Button(SignupFailed, text="OK", command=SignupFailed.destroy)
            WarningMessage.pack()
            ok_button.pack(pady=10)
        else:
        #If all entries are filled it then moves to the actual Sign up Function
            Complete = signup(Email,forename,surname,Password,Subject,Yeargroup,Role_Assigned,Monday,Tuesday,Wednesday,Thursday,Friday,RoomID,Leading)
        if Complete == True:
        #If the Sign Up is successful it moves to the home pahe
            move_to_home()
    else:
        #This is the else statement for an email id that does not end with @ascsdubai.ae
        SignupFailed = tk.Tk()
        SignupFailed.title('Sign Up Failed')
        WarningMessage = ttk.Label(master=SignupFailed, text = 'You have not entered a valid Email for the School!')
        ok_button = tk.Button(SignupFailed, text="OK", command=SignupFailed.destroy)
        WarningMessage.pack()
        ok_button.pack(pady=10)

def BeginLogin():
    #This triggers the log in function through the values entered applying the .strip() function to remove all whitespaces
    Approved = login(EmailEntry.get().strip(),PasswordEntry.get().strip())
    if Approved == True:
        #If the Login is approved then the function triggers to move to the home page 
        move_to_home()

def base_to_signup():
    #This takes us from the home_page to the login page through forgetting the frame associated with the login and the sign up prompts while packing the frame assoiciated with sign up 
    LogIn.forget()
    SignUpButton.forget()
    SignUpPrompt.forget()
    SignUp.pack(padx = 100)

def signup_to_login():
    #The triggers a return to login from sign up through forgetting the Sign Up frame and packing all the values needed to re-establish the inital login part of the base page
    SignUp.forget()
    LogIn.pack(side='top',padx = 100)
    LogIntitle.pack(side='top')
    EmailLabel.pack(pady = 10)
    EmailEntry.pack(pady=5)
    passwordLabel.pack(pady =5)
    PasswordEntry.pack(pady=5)
    LogInSubmit.pack(pady=5)
    SignUpPrompt.pack(pady=15, padx = 100)
    SignUpButton.pack(padx = 100)

    

def move_to_home():
    #Certain variables are established as global variables to be used throughout the program 
    global current_teacher 
    global lesson_start_times
    global current_day
    global year_timetable
    #It checks which email entry is used the login or the signup one and then gets the Email Used to sign up 
    if EmailEntry.get() == '':
        EmailUsed = EmailsignupEntry.get().strip()
    else:
        EmailUsed = EmailEntry.get().strip()
    #All widegts that are not fthe sidebar_frame or title are forgotten in order to clear the page
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget()
    #It then gets the current day and then established the lesson start times for the day along with a repeating value
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    current_date = datetime.now()
    current_day = current_date.strftime("%A")
    if current_day in days:
        if current_day == 'Friday':
            lesson_start_times = ['8:10','8:55','9:40','10:45']
            repeating = 4
        else:
            lesson_start_times = ['07:40', '08:25', '09:10', '10:15', '11:00', '11:45', '13:10', '13:55']
            repeating = 8
    else:
        lesson_start_times = []
        repeating = 0
    #The system then retrievs using the EmailUsed various fields that are assoicated with the teacher at hand
    cursor.execute('''
    SELECT Teacheremail, Forename, Surname, Subject, Year, RoleAssigned, Leading
    FROM Teacher
    WHERE Teacheremail = ?;
    ''', (EmailUsed,))
    result = cursor.fetchone()
    #An object is created associated with that teacher in order to utilise the functions assigned to them with the Role_Assigned deciding whether the object are created as a Head of Year or a normal teacher 
    teacher_email, forename, surname, subject, assigned, Role_Assigned, leading = result
    if Role_Assigned == 'Teacher':
        current_teacher = teacher(teacher_email, f"{forename} {surname}", Role_Assigned, subject, assigned,leading = 'None')
    elif Role_Assigned == 'Head of Year':
        current_teacher = Head_of_Year(teacher_email, f"{forename} {surname}", Role_Assigned, subject, assigned, leading)
    #The home button on the side bar is changed to have the Button Active style to differentiate from other button 
    sidebar_frame.pack(side='left', fill='y')
    homebutton['style'] = 'ButtonActive.TButton'
    #The side bar and title are now packed 
    homebutton.pack(fill=tk.X, pady = 20)
    button1.pack(fill=tk.X, pady = 20)  
    button2.pack(fill=tk.X, pady = 20)
    button3.pack(fill=tk.X, pady = 20)
    button4.pack(fill=tk.X, pady = 20)
    welcometitle['text'] = f'Welcome to the System {current_teacher.name}'
    welcometitle.pack(pady = 5)
    #The home page will also contain the teacher's timetable with it's frame, title and display packed
    Timetable_Frame.pack(pady = 10) 
    TimetableTitle.pack(pady=30)
    Timetable_Display.pack(fill = 'both', expand = True)
    #Making sure there are values in lesson start times it then gets the timetable for the teacher using the timetableread method 
    if lesson_start_times != []:
        TodayTimetable,year_timetable = current_teacher.timetableread(current_day)
    else:
        TodayTimetable = []
        year_timetable = []
    #It now uses the today timetable which contains the actual subjects the teacher is teaching and repeating is used to define iteration limits
    if TodayTimetable != []:
        for i in range(repeating):
            #The start time, lesson and current time is taken in string format
            time = lesson_start_times[i]
            lesson = TodayTimetable[i]
            current_time = datetime.now().time()
            current_time_str = current_time.strftime('%H:%M')
            #This part of the code accounts for lesson which are followed by breaks by setting the next_lesson_start_time to the start time of each break or else the next_lesson_start_time is simply the next value in lesson start times
            try:
                if time == '9:10':
                    next_lesson_start_time = datetime.strptime('9:55', "%H:%M")
                elif time == '11:45':
                    next_lesson_start_time = datetime.strptime('12:30', "%H:%M")
                else:
                    next_lesson_start_time = datetime.strptime(lesson_start_times[i + 1], '%H:%M')
                current_time_datetime = datetime.strptime(current_time_str, '%H:%M')
                #The code checks if the current time is within the timings of the current lesson if it is the timtable displays ongoing if the current time is passed the start time of next lesson the timetable shows finished for that lesson and if the current time is not greater than the next lesson start time unfinished is displayed
                if current_time_datetime < next_lesson_start_time and current_time_datetime >= datetime.strptime(lesson_start_times[i], '%H:%M'):
                    status = 'Ongoing'
                elif current_time_datetime < next_lesson_start_time:
                    status = 'Unfinished'
                else:
                    status = 'Finished'
            #If when it reaches the last lesson start time there is no following lesson start time so an index error will occur so to account for this a seperate part of the code checks for whether the last lesson is over
            except IndexError:
                time_obj = datetime.strptime('14:40', "%H:%M")
                if current_time_datetime < time_obj and current_time_datetime >= datetime.strptime(lesson_start_times[i], '%H:%M'):
                    status = 'Ongoing'
                elif current_time_datetime < time_obj:
                    status = 'Unfinished'
                else:
                    status = 'Finished'   
            #It replaces the None values in the timetable with free
            if lesson is None:
                lesson = 'Free'
            #The Timetable display is updated with the values neccessary 
            Timetable_Display.insert(parent='', index=tk.END, values=(time, lesson, status, year_timetable[i]))



def TimingCheck(student,Timing):
    #The system gets in Timing the leaving time of each student in a dictionary and time it will take for them to arrive to lesson 
    Timing_per_Studnet = Timing
    ExpectedTimeTaken = Timing_per_Studnet[student.id][0]
    #The system then gets the expected time taken for the student by adding time in minutes to the time they left their last class
    ExpectedTimeTaken = (ExpectedTimeTaken//60)
    LeavingTime = Timing_per_Studnet[student.id][1]
    LeavingTime = datetime.strptime(LeavingTime, "%H:%M")
    target_time = LeavingTime + timedelta(minutes=ExpectedTimeTaken)
    return target_time     

def AbsentStudnet(StudentID,TeachersEmail,attendance_id,attendance):
    #A record is added into attendance for an Absent Student where Lateness is set as 99 as a standard 
    cursor.execute('''
            INSERT INTO Attendance(LessonID,Studentemail, Teacheremail, Class_Name, SwipeID, Attendance, Lateness)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (attendance_id,StudentID, str(TeachersEmail),'','', attendance,99))
    


def Attending(StudentID, Present, TeachersEmail,attendance_id,target_time,current_time, attendance):
    #It checks if attendance is Present(P) and if not it then works out how late the student was to lesson
    if attendance != 'P':
        if target_time != 0:
            target_datetime = datetime.strptime(target_time, '%H:%M')
            current_datetime = datetime.strptime(current_time, '%H:%M')
            time_difference = current_datetime -  target_datetime 
            time_difference_in_minutes = max(0, int(time_difference.total_seconds() / 60))
    else:
    #If the student arrived on time and is Present then time differnece is set to 0 as they are not laye and then inserted into the attendance table 
        time_difference_in_minutes = 0
    cursor.execute('''
        INSERT INTO Attendance(LessonID,Studentemail, Teacheremail, Class_Name, SwipeID, Attendance, Lateness)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (attendance_id,StudentID, str(TeachersEmail), Present[2], Present[0], attendance, time_difference_in_minutes))
    return 'Present'

def to_attendance():
    global matches 
    global current_lesson
    #The system forgets all the widgets except the sidebar and title and sets the style of all the buttons in the siderbar to a standard sidebar buttone except for button1 which represents the button on the siderbar that is for attendance
    title['text'] = 'Attendance Marking'
    for child in sidebar_frame.winfo_children():
        if child == button1:  
            child['style'] = 'ButtonActive.TButton'
        else:
            child['style'] = 'SidebarButton.TButton'  
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget()
    #A scrollbar is created on the attendance display 
    vsb = ttk.Scrollbar(window, orient="vertical", command=AttendanceDisplay.yview)
    AttendanceDisplay.configure(yscrollcommand=vsb.set)
    AttendanceDisplay.pack(pady=30)
    vsb.pack(side="right", fill="y") 
    #The system now retirves the studnets for the teacher's current lesson
    if lesson_start_times != []:
        matches, current_lesson = current_teacher.Get_Students_For_Teacher(Student_List, lesson_start_times)
    #The system gets the Room ID for each teacher
    result = get_class_key_by_teacher(current_teacher.emailid)
    end_node = result
    end_node = end_node[0][0]
    #All the variables are set up for the system such as potenital lates, temp2 and temp1
    potentiallates = []
    temp2 = []
    temp1 = matches
    Timings_List_Per_Stuent = {}
    ExpectedArrivalTime = {}
    #The attendance id which will be the id for all the attendance record from a particular class is created
    current_date = dt_date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    attendance_id = formatted_date + '-' + str(current_teacher.emailid) + '-' + str(current_lesson)

    #The system checks first if matches has values then it moves on to check_arrivals where if its id the first lesson of the day the function triggers immediately and if not it checks if the lesson is a double and will not trigger again in the second lesson 
    if matches != []:
        if current_lesson == 0:
            check_arrivals(matches, end_node, potentiallates, temp2, temp1, Timings_List_Per_Stuent, ExpectedArrivalTime, attendance_id, current_lesson)
        else:
            if year_timetable[current_lesson] != year_timetable[current_lesson-1]:
                check_arrivals(matches, end_node, potentiallates, temp2, temp1, Timings_List_Per_Stuent, ExpectedArrivalTime, attendance_id, current_lesson)
            
def Attendance_Display_Begin(event):
    #This function is triggered when pressing a row on the attendance displau
    selected_item = AttendanceDisplay.selection()[0]
    values = AttendanceDisplay.item(selected_item, 'values')
    #It retrives the student_email and thus the object assoicated with the student
    student_email = values[1]
    student = Student_List[student_email]
    #The method of showing all their attendance for the previous lessons of the day is carried out 
    student.Day_Attendance_Display()


def check_arrivals(matches,end_node,potentiallates,temp2,temp1,Timings_List_Per_Stuent,ExpectedArrivalTime,attendance_id,current_lesson):
    global endtime
    #This is the main function of the whole program
    if current_day != 'Friday':
    #It checks if current day is Friday if it is not then it retrieves lesson end time simply by current lesson + 1 in lesson start times however this is not possible for some lesson like the ones before break and the last lesson so excpetion handlers and checks are put in place to make sure right end time is found 
        try:
            endtime = lesson_start_times[current_lesson+1]
            if endtime == '10:15':
                endtime = '09:55'
            elif endtime == '13:10':
                endtime = '12:30'
            else:
                pass
        except:
            endtime = '14:30'
    else:
        #For friday due to the seperate timetable seperate exception and if statements are put into to handle it 
        try:
            endtime = lesson_start_times[current_lesson+1]
            if endtime == '10:45':
                endtime == '10:25'
        except:
            endtime = '11:30'
        #The system now gets current time 
    current_time = datetime.now().strftime("%H:%M")
    if matches != []:
        students_to_remove = []
        students_to_remove2 = []
        students_to_remove3 = []
        for student in temp1:
            #For every student in temp1 it cehcks if they have left their last lesson. This part of the code checks for students that have arrived before the program started 
            Attend = student.Get_Last_Lesson_Leave(current_lesson)
            if Attend == None:
                #If the student has not left their last lesson it checks if the student has arrived to school at all 
                today_date = dt_date.today()
                cursor.execute('''
                    SELECT * FROM Swipe
                    WHERE Studentid = ? AND Class_Name = 'Enterance' AND Date = ? AND SwipeDirection = 1
                    ORDER BY Time
                ''', (student.id, str(today_date)))
                absent_check = cursor.fetchall()
                #If they have not arrived to school it inserts an absent statement into the attendance display for them 
                if absent_check == []: 
                        Check = False
                        for item in AttendanceDisplay.get_children():
                            current_student_id = AttendanceDisplay.item(item, "values")[1]
                            if current_student_id == student.id:
                                Check = True
                        if Check == False:
                            Attendance = 'Absent'
                            AttendanceDisplay.insert(parent='', index=tk.END, values=(Attendance,student.id, student.forename + ' ' + student.surname, student.year))
                        students_to_remove.append(student)
                else:
                    pass
            else:
                #If the student has left their current lesson it checks if they have joined their current lesson and find expected time taken to arrive 
                Present = student.get_current_lesson_join(current_lesson)
                time = graph.Estimated_Arrival_Time(Attend,end_node)
                if Present is None:
                    #If thye have not already arrived it gets the timing_list_per_student values for the student which is their leaving time and expected time taken 
                    Timings_List_Per_Stuent[student.id] = time,Attend[3]
                    #The student is removed from this list and added to the next with the target_time found for the student and stored in the ExpectedArrivalTime dictionary with the email id acting as the key and value being expected time to arrive
                    temp2.append(student)
                    students_to_remove.append(student)
                    target_time = TimingCheck(student,Timings_List_Per_Stuent)
                    ExpectedArrivalTime[student.id] = target_time.strftime("%H:%M")
                else:
                    #If the student has arrived it makes sure there is not an attendance record added for the student
                    cursor.execute('''
                    SELECT * FROM Attendance
                    WHERE Studentemail = ? AND Teacheremail = ? AND LessonID = ?
                    ''', (student.id,current_teacher.emailid,attendance_id))
                    results = cursor.fetchall()
                    if results == []:
                        #If there is no attendance record it gets the start time of the lesson and will compare it to the arrival time of the sutdent
                        Attendance = ''
                        #This part of the code accounts for double lesson with if the lesson being a double it then sets start time as the previous lessons start time
                        if year_timetable[current_lesson] == year_timetable[current_lesson-1]:
                            time1 = datetime.strptime(lesson_start_times[current_lesson-1], "%H:%M")
                        else:
                            time1 = datetime.strptime(lesson_start_times[current_lesson], "%H:%M")
                        #The code now gets the differenne between swipe time and lesson start time and compares that to expected time taken to get whether the Student is Present or Late 
                        time2 = datetime.strptime(Present[3], "%H:%M")
                        time_difference = time2 - time1
                        time_difference = time_difference.total_seconds()
                        current_time = Attend[3]
                        if time_difference > time:
                            Attendance = 'Late'
                            time_difference_minutes = time_difference // 60
                            Eta_datetime = time1 + timedelta(minutes=time_difference_minutes)
                            Eta = Eta_datetime.strftime("%H:%M")
                        elif time_difference <= time:
                            Attendance = 'Present'
                            Eta = lesson_start_times[current_lesson]
                        #An attendance record is then inserted with the values 
                        Placeholder = Attending(student.id,Present,current_teacher.emailid,attendance_id,Eta,current_time,Attendance[0])
                        #The attendance display has a value added with the attendance display being merge sorted as well 
                        AttendanceDisplay.insert(parent='', index=tk.END, values=(Attendance,student.id,student.forename + ' ' + student.surname, student.year))
                        merge_sort_treeview(AttendanceDisplay, 2)
                        students_to_remove.append(student)
                        current_time = datetime.now().strftime("%H:%M")               
                    else:
                        students_to_remove.append(student)
        #Temp 1 is then changed to remove all the students in students_to_remove
        temp1 = [student for student in temp1 if student not in students_to_remove] 
        for student in temp2:
            if len(temp2) == 0:
                break
            #For each student the expected arrival time is retrieved from the dictionary
            Eta = ExpectedArrivalTime[student.id]
            Attendance = 'Absent'
            #If the current time is equal to the expcted arrival time
            if current_time == Eta:
                #Checks if the student has arrived
                Present = student.get_current_lesson_join(current_lesson)
                if Present is None:
                    #If the student has not they are marked as absent and an alert is sent via the Non Arrival tkinter window
                    Attendance = 'Absent'
                    AttendanceDisplay.insert(parent='', index=tk.END, values=(Attendance,student.id, student.forename + ' ' + student.surname, student.year))
                    NonArrival = tk.Tk()
                    NonArrival.title('Student is not in Class!')
                    StudentNotHere = ttk.Label(master=NonArrival, text=f'The student, ID : {student.id} and Name: {student.forename} {student.surname}, is not present in the lesson when they should be!')
                    ok_button = tk.Button(master = NonArrival, text="OK", command=NonArrival.destroy)
                    StudentNotHere.pack()
                    ok_button.pack()
                    merge_sort_treeview(AttendanceDisplay, 2)
                    #The student is added to the potential_lates search now
                    potentiallates.append(student)
                    students_to_remove2.append(student)
                else:
                    #If the student has arrived they marked as present and this is displayed with them being removed from any further checks 
                    Attendance = 'Present'
                    Placeholder = Attending(student.id,Present,current_teacher,attendance_id,Eta,current_time,'P')
                    AttendanceDisplay.insert(parent='', index=tk.END, values=(Attendance,student.id,student.forename + ' ' + student.surname, student.year))
                    merge_sort_treeview(AttendanceDisplay, 2)
                    students_to_remove2.append(student)
        for student in students_to_remove2:
            temp2.remove(student)
        for student in potentiallates:
            #For each student it checks if they have arrived
            Present = student.get_current_lesson_join(current_lesson)
            Eta = ExpectedArrivalTime[student.id]
            existing_item = -1
            if Present is not None:
                #If they have arrived it will add the record into the attendance table
                Attendance = 'Late'
                Placeholder = Attending(student.id, Present,current_teacher.emailid, attendance_id, Eta, current_time, 'L')
                #It now retrieves the index for the student in the attendace display and overwrites the absent value to late
                for item in AttendanceDisplay.get_children():
                    if AttendanceDisplay.item(item, "values")[1] == student.id:
                        existing_item = item
                        break
                if existing_item != -1:
                    AttendanceDisplay.item(existing_item, values=(Attendance, student.id, student.forename + ' ' + student.surname, student.year))
                    students_to_remove3.append(student)
        for student in students_to_remove3:
            potentiallates.remove(student)
    if current_time == endtime:
        #If the lesson end time has been reached it now moves on to the next lesson
        if year_timetable[current_lesson] != year_timetable[current_lesson+1]:
            #If the year timetable has the same value for the next lesson this indicates they are teaching the same year next so the lesson is a double so it doesn't need to reset anything
            for student in potentiallates:
                #Any students who are still in potential lates have not arrived and are marked absent
                AbsentStudnet(student.id,current_teacher.emailid,attendance_id,'A') 
            #If the lesson is followed by a break or end of the day it just wipes all records and then stops the check_arrivals
            if endtime == '09:55' or endtime == '12:30' or endtime == '14:30':
                for child in AttendanceDisplay.get_children():
                    AttendanceDisplay.delete(child)
            else:
                #The end node is gotten again
                end_node = get_class_key_by_teacher(current_teacher.emailid)
                end_node = end_node[0][0]
                #All the studnets for the next lesson and the new current_lesson value is found
                matches, current_lesson = current_teacher.Get_Students_For_Teacher(Student_List, lesson_start_times)
                #All remaining values assoicated with the check_arrivals are reset
                potentiallates = []
                temp2 = []
                temp1 = matches
                #A new lesson id is created in the form 'date-teacher email-current_lesson'
                current_date = dt_date.today()
                formatted_date = current_date.strftime("%Y-%m-%d")
                attendance_id = formatted_date +'-'+str(current_teacher.emailid) +'-'+ str(current_lesson)
                Timings_List_Per_Stuent = {}
                ExpectedArrivalTime ={}
                current_date = datetime.now().date()
                #All records are wiped from Attendance Display
                for child in AttendanceDisplay.get_children():
                    AttendanceDisplay.delete(child)
                #It starts again with the check_arrivals
                check_arrivals(matches,end_node,potentiallates,temp2,temp1,Timings_List_Per_Stuent,ExpectedArrivalTime,attendance_id,current_lesson)       
        else:
            #This else statements handles cases where the lesson is double in this case all values except current lesson are kept same with current_lesson incremented by one and then the program continues recursively calling check arrivals after 20 seconds delay
            current_lesson +=1
            window.after(20000, lambda: check_arrivals(matches,end_node,potentiallates,temp2,temp1,Timings_List_Per_Stuent,ExpectedArrivalTime,attendance_id,current_lesson))   
    else:
        #This else statement if used to handle if end time is not equal to current time it then recursively calls the function again after a delay of 20 seconds 
        window.after(20000, lambda: check_arrivals(matches,end_node,potentiallates,temp2,temp1,Timings_List_Per_Stuent,ExpectedArrivalTime,attendance_id,current_lesson))



def to_analysis():
    #Sets the title of the page to 'Analysis System' and changes the siderbar frame to have the analysis button being the one which has the active style 
    title['text'] = 'Analysis System'
    for child in sidebar_frame.winfo_children():
        if child == button2:  
            child['style'] = 'ButtonActive.TButton'
        else:
            child['style'] = 'SidebarButton.TButton'  
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget()
    if current_teacher.role == 'Head of Year':
    #If the teacher is a head of year a special Analysis Head of Year Label button is packed 
        Analysis_Head_of_Year_Label.pack(side="top", anchor="ne", pady=20)
    Analysis_Student_Button = ttk.Button(master=AnalysisFrame, text='Analyse', style='Submit.TButton', command=current_teacher.subject_specific_student_analysis)
    #The Analysis Title and Analysis Frame are packed with all the associated values with it
    AnalysisTitle.pack(pady=20)
    AnalysisFrame.pack()
    DateTitle.grid(row=0, column=0, pady=10, padx=5, sticky='w')
    calendar.grid(row=0, column=1, pady=10, padx=5, sticky='ew')
    LessonTitle.grid(row=1, column=0, pady=10, padx=5, sticky='w')
    AnalysisLesson.grid(row=1, column=1, pady=10, padx=5, sticky='ew')
    AnalysisButton.grid(row=1, column=2, pady=10, padx=10, sticky='ew')
    #The head of year allows for a wider range of different analysis to be packed whilst a normal teacher gets fewer options
    if current_teacher.role == 'Head of Year':
        SpecificAnalysisTitle.grid(row =2 ,column = 0 ,columnspan = 4, pady = 10)
        StudentTitle.grid(row=3, column=0, pady=10, padx=5, sticky='w')
        AnalysisStudentChoice.grid(row=3, column=1, pady=10, padx=5, sticky='ew')
        Specific_Analysis_Email.grid(row=4, column=0, pady=5, padx=5, sticky='w')
        Specific_Analysis_Email_Entry.grid(row=4, column=1, pady=5, padx=5, sticky='ew')
        Analysis_Student_Button.grid(row=4, column=2, pady=5, padx=10, sticky='ew')
    else:
        #Normal Teachers have just a standard values packed 
        StudentTitle.grid(row=2, column=0, pady=10, padx=5, sticky='w')
        AnalysisStudentChoice.grid(row=2, column=1, pady=10, padx=5, sticky='ew')
        Analysis_Student_Button.grid(row=2, column=2, pady=10, padx=5, sticky='ew')

        
   



def analysis():
    #It forgets the frame showing statistics for the last analysis if applicable
    try:
        StatsFrame.forget()
    except:
        pass
    #Checks if Analysis Lesson Choice has a value 
    if AnalysisLessonChoice.get() != '':
        #If analysis lesson choice has a value it converts the values into the lesson id for the lesson
        lateness_list = []
        lesson_number = ''.join(filter(str.isdigit, AnalysisLessonChoice.get()))
        selected_date = calendar.entry.get().strip()
        selected_date = datetime.strptime(selected_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        lesson_number = int(lesson_number) - 1
        lesson_id = str(selected_date) +'-'+str(current_teacher.emailid) +'-'+str(lesson_number)
        #Here aggregate SQL functions are carried out on all the records retrieved with the specific lesson ID
        cursor.execute('''
        SELECT
            COUNT(CASE WHEN Lateness = 0 THEN 1 END) AS PresentStudents,
            COUNT(CASE WHEN Lateness = 1 THEN 1 END) AS Late1,
            COUNT(CASE WHEN Lateness = 2 THEN 1 END) AS Late2,
            COUNT(CASE WHEN Lateness = 3 THEN 1 END) AS Late3,
            COUNT(CASE WHEN Lateness = 4 THEN 1 END) AS Late4,
            COUNT(CASE WHEN Lateness >= 5 AND Lateness < 99 THEN 1 END) AS Late5Plus,
            COUNT(CASE WHEN Lateness = 99 THEN 1 END) AS AbsentStudents
        FROM Attendance
        WHERE LessonID = ?
    ''', (lesson_id,))
        attendance_records = cursor.fetchall()
        #If the attendance records have been fetches it constructs a graph for this 
        if attendance_records != [(0,0,0,0,0,0,0)]:
            posx = ['0','1','2','3','4','5 beyond','Absent']
            posy = [0,0,0,0,0,0,0]
            posy[0] = attendance_records[0][0]
            posy[1] = attendance_records[0][1]
            posy[2] = attendance_records[0][2]
            posy[3] = attendance_records[0][3]
            posy[4] = attendance_records[0][4]
            posy[5] = attendance_records[0][5]
            posy[6] = attendance_records[0][6]
            #Further Aggregate SQL is carried out to get certain statistics such as Present Students, Absent Students, Average Lateness etc. 
            cursor.execute('''
            SELECT
                COUNT(CASE WHEN Lateness = 0 THEN 1 END) AS PresentStudents,
                COUNT(CASE WHEN Lateness > 0 AND Lateness < 99 THEN 1 END) AS LateStudents,
                COUNT(CASE WHEN Lateness = 99 THEN 1 END) AS AbsentStudents,
                AVG(CASE WHEN Lateness > 0 AND Lateness < 99 THEN Lateness END) AS AverageLateness,
                GROUP_CONCAT(CASE WHEN Lateness < 99 THEN Lateness END, ',') AS LatenessList
            FROM Attendance
            WHERE LessonID = ?
            ''', (lesson_id,))
            result = cursor.fetchone()
            present_students = result[0]
            late_students = result[1]
            absent_students = result[2]
            average_lateness = result[3]
            lateness_list_str = result[4]
            #This code gets all the lateness values and then carries out a bubble sort on them to find the median lateness
            lateness_list = []
            if lateness_list_str:
                lateness_strings = lateness_list_str.split(',')
                for lateness_str in lateness_strings:
                    lateness_list.append(int(lateness_str))
        
            n = len(lateness_list)
            for i in range(n - 1):
                for j in range(0, n - i - 1):
                    if lateness_list[j] > lateness_list[j + 1]:
                        lateness_list[j], lateness_list[j + 1] = lateness_list[j + 1], lateness_list[j]
            if n > 0:
                median_lateness = lateness_list[n // 2]
            else:
                median_lateness = 0
        
            #The stats frame is configured with all the values needed and packed
            PresentStudentsLabel['text'] = f'Amount of Students Present:{str(present_students)}'
            LateStudentsLabel['text'] = f'Amount of Students Late: {str(late_students)}'
            AbsentStudentsLabel['text'] = f'Amount of Students Absent:{str(absent_students)}'
            Average_Student_Lateness['text'] = f'Average Student Lateness {str(average_lateness)}'
            Median_Student_Lateness['text'] = f'Median Student Lateness {str(median_lateness)}'
            StatsFrame.pack(padx = 10, side = tk.LEFT)
            PresentStudentsLabel.pack()
            LateStudentsLabel.pack()
            AbsentStudentsLabel.pack()
            Average_Student_Lateness.pack()
            Median_Student_Lateness.pack()
            #The bar graph is now plotted
            plt.bar(posx,posy)
            plt.xlabel('Lateness (minutes)')
            plt.ylabel('Number of Students')
            plt.title('Lateness Distribution for Lesson')
            plt.show()
        else:
            #If no record is retrieved for the lesosn a message is outputted informing the user of this 
            NoRecord = tk.Tk()
            WarningMessage = ttk.Label(master=NoRecord, text = 'No records stored for date and lesson provided')
            ok_button = tk.Button(NoRecord, text="OK", command=NoRecord.destroy)
            WarningMessage.pack()
            ok_button.pack()
    else:
        #If attendance lesson choice has no value then an input_error() is carried out 
        input_error()       

def HOY_Analysis():
    #This is all of the analysis available to the Head of Year it is triggered through the pressing of the Head of Year button
    try:
        StatsFrame.forget()
        Head_of_Year_Menu.forget()
    except:
        pass
    global WeekSubmit
    global SubjectAnalysis_Button
    global HOY_Student_Submit
    #The 4 analysis avilable to only head of years are created and then stored as global variables 
    WeekSubmit = ttk.Button(master=Head_of_Year_Menu, text='Submit', command=current_teacher.WeekAnalysis, style = 'Submit.TButton')
    SubjectAnalysis_Button = ttk.Button(master=Head_of_Year_Menu,text='Submit', command = current_teacher.subject_analysis, style = 'Submit.TButton')
    HOY_Student_Submit = ttk.Button(master=Head_of_Year_Menu,text='Submit', command = current_teacher.student_analysis, style = 'Submit.TButton')
    Congregation_Button = ttk.Button(master = Head_of_Year_Menu, text = 'Congregation Analysis', command = current_teacher.congregation_analysis, style = 'Standard.TButton' )
    Head_of_Year_Menu.pack(pady = 10)
    #The head of year menu is made with button's packed
    WeekAnalysisButton.pack(side='top', padx=25)
    SubjectAnalysisButton.pack(side='left', padx=20)
    StudentAnalysisButton.pack(side='right', padx=20, pady= 20)
    Congregation_Button.pack(side='bottom', pady=25)

#The analysis below handling the tkinter values so the Head of Year objects methods can be easily carried out without handling tkinter 
def WeekAnalysisEntry():
    #This creates the widgets needed to enter the values for Week Analysis Entry
    widgets_to_remove = [WeekLabel, Startcalendar, Endcalendar, WeekSubmit, HOY_Student_Label, HOY_Student_Code, HOY_Student_Submit, SubjectAnalysis_Label, SubjectAnalysis_Entry, SubjectAnalysis_Button]
    for widget in widgets_to_remove:
        widget.pack_forget()
    WeekLabel.pack(pady = 10)
    Startcalendar.pack()
    Endcalendar.pack()
    WeekSubmit.pack()

def studentanalysisentry():
    #This creates the widgets neccessary for a student analysis 
    widgets_to_remove =  [WeekLabel, Startcalendar, Endcalendar, WeekSubmit, HOY_Student_Label, HOY_Student_Code, HOY_Student_Submit, SubjectAnalysis_Label, SubjectAnalysis_Entry, SubjectAnalysis_Button]
    for widget in widgets_to_remove:
        widget.pack_forget()
    HOY_Student_Label.pack(pady = 10)
    HOY_Student_Code.pack()
    HOY_Student_Submit.pack()

def subjectanalysisentry():
    #This creates the widgets for a subject analysis
    widgets_to_remove =  [WeekLabel, Startcalendar, Endcalendar, WeekSubmit, HOY_Student_Label, HOY_Student_Code, HOY_Student_Submit, SubjectAnalysis_Label, SubjectAnalysis_Entry, SubjectAnalysis_Button]
    for widget in widgets_to_remove:
        widget.pack_forget()
    SubjectAnalysis_Label.pack(pady = 10)
    SubjectAnalysis_Entry.pack()
    SubjectAnalysis_Button.pack()





def to_finder():
    #The title is configured to show the searching system with the siderbar configured to show the finder button as the active button
    title['text'] = 'Searching System'
    for child in sidebar_frame.winfo_children():
        if child == button3:  
            child['style'] = 'ButtonActive.TButton'
        else:
            child['style'] = 'SidebarButton.TButton'
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget()
    #The widgets for the retrieving of the student's last record  are established and packed
    StudentSearchTitle = ttk.Label(master=window,text='Enter the Student ID of the Student you would like to find', font = 'Roboto 24')
    id = tk.StringVar()
    StudentSearch = ttk.Entry(master=window,textvariable=id)
    #The id variable is used to pass the student id into the FindStudnet function 
    StudentSearchSumbit = ttk.Button(master=window,text='Search',command= lambda:FindStudent(id), style = 'Submit.TButton')
    StudentSearchTitle.pack(pady = 10)
    StudentSearch.pack(pady = 5)
    StudentSearchSumbit.pack(pady = 5)


def FindStudent(id):
    #It first makes sure the id has a value 
    if id.get().strip() == '':
        input_error() 
    else:
        try:
            #If there are already any values displayed from the last retrieval of a studnet's latest record it forgets them 
            PotentialNodes.forget()
            DisplayRecord.forget()
            canvas_widget.forget()
        except:
            pass
        #It then carries out the FindingSystem Function
        Status, Record = FindingSystem(id.get().strip())
        if Record == 'None':
            #If there is no record it then configures the display record label 
            DisplayRecord.config(text='No Record Found')
        else:
            #If there is a value it then configures the studnet's retrieved values 
            Student = Student_List[id.get().strip()]
            Name = Student.forename + ' ' + Student.surname
            DisplayRecord.config(text='The Student has been found, ' + Name + ' ' + Status +
                                        ' class ' + Record[4] + ' at time ' + Record[3])
        DisplayRecord.pack(pady=10)
        #It checks if staus is left or attempted to enter so if the last record of a student tells us they are not in a class
        if Status == 'Left' or Status == 'Attempted to Enter':
            #If they are not in a class it gets the time difference between current time and time of last swipe and carries out the iterative deepening search on this
            current_time = datetime.now()
            start_time = datetime.strptime(Record[3], '%H:%M')
            time_difference = current_time - start_time
            seconds_difference = time_difference.seconds 
            #Preventing a too long search
            if seconds_difference > 200:
                PotentialNodes['text'] = 'The system is unable to find the student\'s exact position'
                PotentialNodes.pack()
            else:
                potential_nodes = graph.time_dependent_ids(Record[4], seconds_difference)
                #If there are no potential nodes or too many potntial nodes it says the system cannot find the exact position
                if potential_nodes == [] or len(potential_nodes) > 10:
                    PotentialNodes['text'] = 'The system is unable to find the student\'s exact position'
                    PotentialNodes.pack()
                else:
                    #If there are enough nodes to be reliable the display_graph function is carried out 
                    PotentialNodes['text'] = f'After analysis, the student is potentially near {potential_nodes}'
                    PotentialNodes.pack()
                    display_graph(potential_nodes)
                

       
         
def display_graph(nodes_to_highlight):
    # A graph is crated from the networkx library this will be used to model the school actual floor plan
    G = nx.Graph()
    #The nodes of the graph are made 
    nodes = ['SF054', 'T1', 'SF053', 'SF055', 'SF052', 'SF051', 'E6', 
         'SF048', 'SF044', 'SF047', 'SF043', 'E4', 'TR1', 'TR2', 
         'SF012', 'E3', 'SF011', 'SF013', 'SF014', 'SF010', 'SF015', 'SF009', 
         'T2', 'SF018', 'SF017', 'SF008', 'SF007', 'SF006', 'SF026', 'SF005', 
         'E1', 'SF004', 'SF003', 'SF002', 'SF034', 'SF001', 'FF061', 'P1', 'C1', 
         'L1', 'P2', 'FF014', 'FF013', 'FF012', 'FF011', 
         'FF010', 'FF009', 'FF008', 'FF004', 'FF007', 'FF001','C2','T3','','  ',
         '   ','E4 ','E1 ','E3 ','FF005']
    #Certian nodes are blanks and are just placeholders in order to help construct the graph in a visually appealing manner 
    visible_nodes = []
    placeholder_nodes = []
    
    for node in nodes:
        if node != '' or node != '  ' or node != '   ':
            visible_nodes.append(node)
        else:
            placeholder_nodes.append(node)
    #The nodes are then added to the graph
    G.add_nodes_from(visible_nodes)
    
    G.add_nodes_from(placeholder_nodes)
    #The edges are added in between the nodes
    G.add_edges_from([('SF054', 'SF053'), ('SF053', 'SF052'), 
                      ('SF051', 'SF052'), ('SF051', 'SF048'), 
                      ('SF048', 'SF047'), ('SF054', 'T1'), 
                      ('T1', 'SF055'), ('SF055', 'E6'), 
                      ('E6', 'SF044'), ('SF044', 'SF043'), 
                      ('TR1','TR2'),('SF043','SF042'),
                      ('SF041','SF042'),('SF041','SF040'),
                      ('SF040','E4'), ('E4','E3'),
                      ('TR2','SF012'),('SF012','SF013'),
                      ('SF013','SF014'), ('SF014','SF015'),('E3','SF011'),('SF011','SF010'),
                      ('SF010','SF009'),('SF015','SF018'),('SF018','SF017'),('SF009','T2'),
                      ('SF017','SF008'),('SF007','SF008'),('SF007','SF006'),('SF006','SF005'),
                      ('SF005','SF003'),('SF003','SF002'),('SF002','SF001'),('SF001','SF034'),('SF034','E1'),
                      ('E1','SF026'),('SF026','T2'), ('SF047',''),('','TR1'),
                      ('P2','P1'), ('P1','FF061'), ('L1','P2'),('L1','E4 '),
                      ('FF061','  '),('C1','C2'), ('C2','E3 '),('E3 ','T3'),
                      ('FF014','FF013'),('FF013','FF012'),('FF012','FF011'),('FF011','FF010'),
                      ('FF010','FF009'),('FF009','FF008'),('FF008','FF004'),('FF004','FF001'),
                      ('FF007','E1 '),('E1 ','T3'), ('C1','E4 '), ('FF001','FF005'),('FF005','FF007'),
                      ('  ', '   '), ('FF014', '   ')
                      ])
    #The position of the nodes are set according to x,y coordinates 
    pos = {'SF054': (15, 9), 'SF053': (15, 7), 'SF052': (15, 6), 'SF051': (15, 5),
           'SF048': (15, 4), 'SF047': (15, 3), 'SF043': (13, 3), 'SF044': (13, 4),
           'SF055': (13, 7), 'T1': (13, 8), 'E6': (13, 5), '':(15,1),
           'SF042':(12,2), 'SF041':(11,2), 'SF040':(10,2), 'E4':(9,2), 'TR1':(9,1),
           'TR2':(8,1), 'SF012':(7,1), 'SF013':(6,1), 'SF014':(5,1), 'SF015':(4,1),
           'SF018':(3,0), 'E3':(7,2), 'SF011':(6,2), 'SF010':(5,2),'SF009':(4,2),
           'T2':(3,2), 'SF017':(1,0), 'SF008':(1,2),'SF007':(1,3), 'SF006':(1,4),'SF005':(1,5),
           'SF004':(1,6), 'SF003':(1,7), 'SF002':(1,8), 'SF001':(1,9), 'SF034':(3,9),
           'E1':(3,7.5), 'SF026':(3,4.5), 'FF001':(17,9), 'FF004':(17,8), 'FF008': (17,7),
           'FF009':(17,6),'FF010':(17,5),'FF011':(17,4),'FF012':(17,3),'FF013':(17,2),'FF014':(17,0),
           'FF007': (19,8), 'FF005':(19,9) ,'E1 ':(19,7), 'T3':(19,2), 'E3 ':(22,2), 'C2':(23,2), 'C1':(24,2),       
           'E4 ':(25,2), 'L1': (27,2), 'P2':(27,1), 'P1':(26,1), 'FF061':(25,1),
           '  ':(19,1), '   ':(19,0)
           }
    #The system plots the graph 
    fig, ax = plt.subplots(figsize=(14, 6))
    node_colors = []
    #It then while setting node color checks if they are in node_to_highligt which is the same as potential nodes and colors them yellow to make them stand out
    for node in G.nodes():
        if node in nodes_to_highlight:
            node_colors.append('yellow')  
        elif node == '':
            node_colors.append('white')
        else:
            node_colors.append('white')
    #The graph is the plotted and added to a canvas widget
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax)
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_color='black', font_size=6,ax=ax)
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)






def to_settings():
    #It configures the title to show Settings and the Siderbar to set the settings button as active on it.
    title['text'] = 'Settings'
    for child in sidebar_frame.winfo_children():
        if child == button4:  
            child['style'] = 'ButtonActive.TButton'
        else:
            child['style'] = 'SidebarButton.TButton'
    #All widgets excluding the title and sidebar are forgotten
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget()
    #The canvas with the profile picture is packed
    canvas3.pack(pady = 10) 
    ProfileLabel.pack()
    canvas3.create_image(0, 0, anchor=tk.NW, image=profile_photo)
    #If there are no values in the Email and Name entry of the settings page it adds values into it
    if UserEmailEntry.get() == '':
        UserEmailEntry.insert(0,str(current_teacher.emailid))
    if Name_Entry.get() == '':
        Name_Entry.insert(0,str(current_teacher.name))
    #It then sets the Subject Combobox's value to the subject the teacher is teaching
    SubjectsBox2.set(str(current_teacher.subject))
    #It then checks the year groups the teacher is teaching and updates the values of the variables assigned to it's widgets to represent them as selected
    assigned_numbers = [int(num) for num in current_teacher.assigned.split(',')]
    if 10 in assigned_numbers:
        Year10_Update.set(1)
    if 11 in assigned_numbers:
        Year11_Update.set(1)
    if 12 in assigned_numbers:
        Year12_Update.set(1)
    if 13 in assigned_numbers:
        Year13_Update.set(1)
    #The settings frame is packed with all the widgets with the .grid placement method used to help improve it's visual appeal
    SettingsFrame.pack(pady=10)
    UserEmailLabel.grid(row=0, column=0, sticky='w', pady=5, padx = 10)
    UserEmailEntry.grid(row=0, column=1, pady=5, padx = 10)
    UpdateEmail.grid(row=0, column=2, pady=5, padx = 10)
    UserNameLabel.grid(row=1, column=0, sticky='w', pady=5, padx = 10)
    Name_Entry.grid(row=1, column=1, pady=5, padx = 10)
    Name_Update.grid(row=1, column=2, pady=5, padx = 10)
    User_Subject_Label.grid(row=2, column=0, sticky='w', pady=5, padx = 10)
    SubjectsBox2.grid(row=2, column=1, pady=5, padx = 10)
    Subject_Update.grid(row=2, column=2, pady=5, padx = 10)
    Update_Year_Label.grid(row=3, column=0, sticky='w', pady=5, padx = 10)
    Year12_Update_Box.grid(row=3, column=3, pady=5, padx = 10)
    Year13_Update_Box.grid(row=3, column=4, pady=5, padx = 10)
    Year10_Update_Box.grid(row =3, column =1, pady = 5 ,padx = 10)
    Year11_Update_Box.grid(row =3, column =2, pady = 5 ,padx = 10)
    Year_Update.grid(row=3, column=6, pady=5, padx = 10)
    UpdatePasswordLabel.grid(row=4, column=0, columnspan=4, sticky='w', pady=5, padx = 10)
    InitalPasswordLabel.grid(row=5, column=0, sticky='w', pady=5, padx = 10)
    InitalPasswordEntry.grid(row=5, column=1, pady=5, padx = 10)
    InitalPasswordButton.grid(row=5, column=2, pady=5, padx = 10)

def CheckPassword(Password):
    #This is used as part of the update password part of the program
    Password = Hashing(Password)
    email = current_teacher.emailid
    #The system checks if the password entered matches the password of the user stored
    cursor.execute('''
    SELECT Password
    FROM Teacher
    WHERE Teacheremail = ?
    ''', (email,))
    stored_password = cursor.fetchone()
    #If the password is not found it handles that situatione else it checks if the stored_password matches the password entered
    if stored_password == None:
        WrongPassword = tk.Tk()
        WrongPassword.title('No Password Found')
        WarningMessage = ttk.Label(master=WrongPassword, text = 'No Password Found!')
        ok_button = tk.Button(master = WrongPassword, text="OK", command=WrongPassword.destroy)
        WarningMessage.pack()
        ok_button.pack(pady=10)
    else: 
        #If the password match it packs the tkinter widgets needed for entering the new password   
        if stored_password[0] == Password:
            NewPasswordLabel.grid(row=6, column=0, sticky='w', pady=5, padx = 10)
            NewPasswordEntry.grid(row=6, column=1, pady=5, padx = 10)
            NewPasswordSumbit.grid(row=6, column=2, pady=5, padx = 10)
        else:
            #If they don't match it then sends a warning to the user
            WrongPassword = tk.Tk()
            WrongPassword.title('Passwrod Incorrect')
            WarningMessage = ttk.Label(master=WrongPassword, text = 'Incorrect Password Entry!')
            ok_button = tk.Button(master = WrongPassword, text="OK", command=WrongPassword.destroy)
            WarningMessage.pack()
            ok_button.pack(pady=10)


def Update_Email():
    #To update Email it gets the new email the user enters and updates all record relevant to the teacher's email as well as the object itself
    NewEmail = UserEmailEntry.get().strip()
    if NewEmail == '':
        input_error()
    #It makes sure email ends with the valid value needed
    elif NewEmail.endswith('@alsalamcommunity.ae'):
        cursor.execute("UPDATE Teacher SET Teacheremail = ? WHERE Teacheremail = ?", (NewEmail, current_teacher.emailid))
        cursor.execute("UPDATE Attendance SET Teacheremail = ? WHERE Teacheremail = ?", (NewEmail, current_teacher.emailid))
        connection.commit()
        current_teacher.emailid = NewEmail
    else:
        IncorrectEmail = tk.Tk()
        IncorrectEmail.title('Invalid Email entered')
        WarningMessage = ttk.Label(master=IncorrectEmail, text = 'Incorrect/Invalid Email Entry!')
        ok_button = tk.Button(master = IncorrectEmail, text="OK", command=IncorrectEmail.destroy)
        WarningMessage.pack()
        ok_button.pack(pady=10)


def update_name():
    # When updating name, it gets the name they entered before updating the teacher table and updating the object
    if Name_Entry.get() == '':
        input_error()
    else:
        new_forename, _, new_surname = Name_Entry.get().strip().partition(' ')
        cursor.execute('UPDATE Teacher SET Forename = ?, Surname = ? WHERE Teacheremail = ?', (new_forename, new_surname, current_teacher.emailid))
        connection.commit()
        current_teacher.name = Name_Entry.get().strip()

def update_subject():
    #The teacher table and object are updated with the new subject the teacher teaches
    NewSubject = SubjectsBox2.get()
    cursor.execute('UPDATE Teacher SET Subject = ? WHERE Teacheremail = ?', (NewSubject, current_teacher.emailid))
    connection.commit()
    current_teacher.subject = NewSubject

def update_year():
    #The new list of year groups the teacher is teaching is obtained
    Yeargroup = ''
    if Year12_Update.get() == 1:
        Yeargroup += '12'
    if Year13_Update.get() == 1:
        if Yeargroup != '':
            Yeargroup += ','
        Yeargroup += '13'
    if Year10_Update.get() == 1:
        if Yeargroup != '':
            Yeargroup += ','
        Yeargroup += '10'
    if Year11_Update.get() == 1:
        if Yeargroup != '':
            Yeargroup += ','
        Yeargroup += '11'
    #The new assigned year groups is updated in the teacher table and teacher object
    cursor.execute('UPDATE Teacher SET Year = ?  WHERE Teacheremail = ?', ( Yeargroup, current_teacher.emailid))
    connection.commit()
    current_teacher.assigned = Yeargroup


def to_home():
    global current_day
    #The system configures title to say home page and the siderbar button to have homebutton as active
    title['text'] = 'Home Page'
    for child in sidebar_frame.winfo_children():
        if child == homebutton:  
            child['style'] = 'ButtonActive.TButton'
        else:
            child['style'] = 'SidebarButton.TButton' 
    for widget in window.winfo_children():
        if widget != sidebar_frame and widget != title:
            widget.forget() 
    #It wipes all values from the timetable_display
    for item in Timetable_Display.get_children():
        Timetable_Display.delete(item)
    #It now gets the current day and then establishes the lesson start times
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    current_date = datetime.now()
    current_day = current_date.strftime("%A")
    if current_day in days:
        if current_day == 'Friday':
            lesson_start_times = ['08:10','08:55','09:40','10:45']
            repeating = 4
        else:
            lesson_start_times = ['07:40', '08:25', '09:10', '10:15', '11:00', '11:45', '13:10', '13:55']
            repeating = 8
    else:
        lesson_start_times = []
        repeating = 0
    #It now pack the timetable frame, title and display to show the timetable
    Timetable_Frame.pack() 
    TimetableTitle.pack(pady=30)
    Timetable_Display.pack()
    #It then gets the timetable for the day for both the subjects and year group being taught
    if current_day in days:
        TodayTimetable,year_timetable = current_teacher.timetableread(current_day)
    #It now gets the current time
    current_time = datetime.now().time()
    current_time_str = current_time.strftime('%H:%M')
    for i in range(repeating):
        time = lesson_start_times[i]
        lesson = TodayTimetable[i]
        current_time = datetime.now().time()
        current_time_str = current_time.strftime('%H:%M')
        try:
            #The system gets the end time for each lesson by checking the next lesson start time but for certain lesson like before break it sets a specific end time time value
            if time == '9:10':
                next_lesson_start_time = datetime.strptime('9:55', "%H:%M")
            elif time == '11:45':
                next_lesson_start_time = datetime.strptime('12:30', "%H:%M")
            else:
                next_lesson_start_time = datetime.strptime(lesson_start_times[i + 1], '%H:%M')
            #The system now gets if the lesson is done, ongoing or unfinished meaning not started
            current_time_datetime = datetime.strptime(current_time_str, '%H:%M')
            if current_time_datetime < next_lesson_start_time and current_time_datetime >= datetime.strptime(lesson_start_times[i], '%H:%M'):
                status = 'Ongoing'
            elif current_time_datetime < next_lesson_start_time:
                status = 'Unfinished'
            else:
                status = 'Finished'
        except IndexError:
            #If the last lesson is reached the end time value is set and once again checks if the lesson is comlpete or not
            time_obj = datetime.strptime('14:40', "%H:%M")
            if current_time_datetime < time_obj and current_time_datetime >= datetime.strptime(lesson_start_times[i], '%H:%M'):
                status = 'Ongoing'
            elif current_time_datetime < time_obj:
                status = 'Unfinished'
            else:
                status = 'Finished'   
        if lesson is None:
            lesson = 'Free'
        Timetable_Display.insert(parent='', index=tk.END, values=(time, lesson, status, year_timetable[i]))

def timetable_update_entry(event):
    #It deletes any records needed for a timetable update that are already there
    try:
        Timetable_Update_Subject.delete(0, tk.END)
        Timetable_Update_Year.delete(0, tk.END)
        Timetable_Update_Frame.forget()
    except:
        pass
    #It gets the row which was clicked and the values in it
    item_id = Timetable_Display.identify_row(event.y)  
    data_in_row = Timetable_Display.item(item_id, 'values')
    row_id = Timetable_Display.index(item_id) 
    time = data_in_row[0]
    subject = data_in_row[1]
    year_group = data_in_row[3]
    #The system now creates the widgets shwoing the submit button, subject for the lesson and year for the lesson and packs the valueus
    Timetable_Update = ttk.Button(master=Timetable_Update_Frame, text='Submit', style='Submit.TButton', command=lambda row=row_id: timetable_update(row))
    Timetable_Update_Subject.insert(0,subject)
    Timetable_Update_Year.insert(0,year_group)
    Timetable_Update_Label.grid(row=0, column=0, pady=10, columnspan=2)
    Timetable_Subject_Update_Label.grid(row=1, column=0, padx=10, sticky='e')
    Timetable_Update_Subject.grid(row=1, column=1, padx=10, sticky='w')
    Timetable_Year_Update_Label.grid(row=2, column=0, padx=10, sticky='e')
    Timetable_Update_Year.grid(row=2, column=1, padx=10, sticky='w')
    Timetable_Update.grid(row=3, column=0, columnspan=2, pady=10)
    Timetable_Update_Frame.pack()



def timetable_update(row_id):
    # When submit is pressed in the previous function it makes sure the entries updated actually have values
    if Timetable_Update_Subject.get() == '' or Timetable_Update_Year.get() == '':
        input_error()
    else:
        # It gets the new values created and the current timetable
        new_value = f'{Timetable_Update_Subject.get()}-{Timetable_Update_Year.get()}'
        cursor.execute(f"SELECT {current_day}Timetable FROM Teacher WHERE TeacherEmail = ?", (current_teacher.emailid,))
        current_timetable = cursor.fetchone()[0]
        timetable_list = current_timetable.split(',')
        if 0 <= row_id < len(timetable_list):
            # Update the timetable list with the new value
            timetable_list[row_id] = new_value
            updated_timetable = ','.join(timetable_list)
            # Update the timetable in the database
            cursor.execute(f'UPDATE Teacher SET {current_day}Timetable = ? WHERE TeacherEmail = ?', (updated_timetable, current_teacher.emailid))
            connection.commit()
            # Update the corresponding row in the Timetable_Display widget
            all_values = []
            for item in Timetable_Display.get_children():
                values = Timetable_Display.item(item, 'values')
                all_values.append(values)
            Original_Values = all_values[row_id]
            Time = Original_Values[0]
            Status = Original_Values[2]
            New_Values = [Time,Timetable_Update_Subject.get(),Status,Timetable_Update_Year.get()]
            all_values[row_id] = New_Values
            Timetable_Display.delete(*Timetable_Display.get_children())
            for value in all_values:
                Timetable_Display.insert('', 'end', values=value)
        # Hide the update frame
        Timetable_Update_Frame.forget()




        
#A window is created for the application
window = tk.Tk()

#The style is imported from ttk
style = ttk.Style()

#The window title is established
window.title('Student Attendance Tracking System')

#The styles that will be used throughout the program are established 
button_font = font.Font(family='Helvitica', size=12)
style.configure("Submit.TButton", background='#45b592', foreground='#ffffff', font=button_font, padding=(5, 5))
style.configure('SidebarButton.TButton', background = '#223EB2', foreground = 'white' , font = button_font)
style.configure('Sidebar.TFrame', background = '#223EB2')
style.configure('ButtonActive.TButton', background = '#E92380', foreground = 'white' , font = button_font)
style.configure("Custom.Treeview.Heading", font=('Helvetica', 20, 'bold'), foreground='black',background = '#CDCDCD')
style.configure("Custom.Treeview", highlightthickness=0, bd=0, font=('Helvetica', 14), spacing=10, rowheight = 30)
style.configure('Standard.TButton', background='#FA8072', foreground= 'white', font=button_font, padding=(5, 5 ))

#The screen's geometry is set 
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
screen_height=str(screen_height)
screen_width=str(screen_width)
screen = screen_width+"x"+screen_height
window.geometry(screen)

#The title is created
title = ttk.Label(master = window,text='Welcome to the Student Attendance Tracking System', font='Roboto 40', background = '#223EB2', foreground ='white', anchor='center', justify='center' )
title.pack(fill=tk.X, ipady=20)

#A canvas is created which contains an image that will be used in the base page to help enhance it's visual appeal
canvas = tk.Canvas(window, width=window.winfo_screenwidth() // 2, height=window.winfo_screenheight()-100, bg="white")
canvas.pack(side='left')
pictures_directory = os.path.abspath('BG1.jpg')
original_image = Image.open(pictures_directory)
resized_image = original_image.resize((canvas.winfo_reqwidth(), canvas.winfo_reqheight()))
bg_photo = ImageTk.PhotoImage(resized_image)
canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)

#A second canvas is created which also has an image this being the image of the school's logo
canvas2 = tk.Canvas(window, width=138, height=105)
canvas2.place(x=0, y=0)  
pictures_directory2 = os.path.abspath('Logo2.png')
original_image2 = Image.open(pictures_directory2)
resized_image2 = original_image2.resize((138, 105))
logo_photo = ImageTk.PhotoImage(resized_image2)
canvas2.create_image(0, 0, anchor=tk.NW, image=logo_photo)

#A third canvas is created to hold the profile picture image
canvas3 = tk.Canvas(window, width=350, height=300)
pictures_directory3 = os.path.abspath('ProfilePicture.png')
original_image3 = Image.open(pictures_directory3)
resized_image3 = original_image3.resize((350, 300))
profile_photo = ImageTk.PhotoImage(resized_image3)

#The Sign Up / Log In tkinter widgets are created for 
SignUpLoginFrame = ttk.Frame(master=window)
LogIn = ttk.Frame(master=SignUpLoginFrame,borderwidth = 4)
LogIntitle = ttk.Label(master=LogIn,text='Log In to the System',font='Roboto 28')
EmailLabel = ttk.Label(master=LogIn,text='Enter your Email', font= 'Roboto 18')
EmailEntry = ttk.Entry(master=LogIn)
passwordLabel = ttk.Label(master=LogIn,text='Enter your Password', font = 'Roboto 18')
PasswordEntry = ttk.Entry(master=LogIn,show='*')
LogInSubmit = ttk.Button(master=LogIn,text='Submit', style = 'Submit.TButton', command = BeginLogin)
SignUpButton = ttk.Button(master=SignUpLoginFrame,text='Sign Up',command=base_to_signup, style = 'Standard.TButton')
SignUpPrompt = ttk.Label(master=SignUpLoginFrame, text='Don\'t have an account? Sign Up Below!', font='bold')
UserWarningMessage = ttk.Label(master = window)

#These values established are now packed so they are seen in the base page
SignUpLoginFrame.pack(side = 'right')
LogIn.pack(side='top',padx = 100)
LogIntitle.pack(side='top')
EmailLabel.pack(pady = 10)
EmailEntry.pack(pady=5)
passwordLabel.pack(pady =5)
PasswordEntry.pack(pady=5)
LogInSubmit.pack(pady=5)
SignUpPrompt.pack(pady=15, padx = 100)
SignUpButton.pack(padx = 100)



#The tkinter widgets for Sign Up are now also created
SignUp = ttk.Frame(master=SignUpLoginFrame)
SignUpTitle = ttk.Label(master=SignUp,text = 'Sign Up', font='Roboto 28')

Email = ttk.Label(master=SignUp,text='Enter your Email', font = 'Roboto 10')
EmailsignupEntry = ttk.Entry(master=SignUp)

name = ttk.Label(master=SignUp,text='Enter your name', font = 'Roboto 10')
nameEntry = ttk.Entry(master=SignUp)


subjectlabel = ttk.Label(master=SignUp,text='What Subject do you teach', font = 'Roboto 10')
subjects = ['Maths','Physics','Biology','Chemistry','Computer Science']
SubjectsBox = ttk.Combobox(master=SignUp)
SubjectsBox['values'] = subjects

YearLabel = ttk.Label(master=SignUp,text='What Year Groups are you teaching?', font = 'Roboto 10')
Year12 = tk.IntVar(value=0)
Year13 = tk.IntVar(value=0)
Year10 = tk.IntVar(value=0)
Year11 = tk.IntVar(value=0)
year12 = ttk.Checkbutton(master=SignUp, text='Year 12', variable=Year12)
year13 = ttk.Checkbutton(master=SignUp, text='Year 13', variable=Year13)
year11button = ttk.Checkbutton(master=SignUp,text='Year 11', variable = Year11)
year10button = ttk.Checkbutton(master=SignUp,text='Year 10', variable = Year10)

RoleAssignedLabel = ttk.Label(master=SignUp,text='Are you Teacher or a Head Of Year', font = 'Roboto 10')
RoleAssigned = ttk.IntVar(value=0)
Teacher = ttk.Radiobutton(master=SignUp,text='Teacher',value=1,variable=RoleAssigned)
Head_of_Year_Pick = ttk.Radiobutton(master=SignUp,text='Head of Year',value=2,variable=RoleAssigned)

RoomLabel = ttk.Label(master = SignUp,text = 'What is the ID of the Room you will occupy', font = 'Roboto 10')
RoomEntry = ttk.Entry(master = SignUp)

LeadingLabel = ttk.Label(master=SignUp,text = 'If Head of Year which year group do you Lead', font = 'Roboto 10')
LeadingEntry = ttk.Entry(master=SignUp)

TimetableLabel = ttk.Label(master=SignUp,text='Enter your Timetable Format Example: Maths-12,Maths-11...', font = 'Roboto 10')
Monday = ttk.Label(master=SignUp,text='Enter Mondays Timetable', font = 'Roboto 10')
MondayEntry =ttk.Entry(master=SignUp)
Teusday = ttk.Label(master=SignUp,text='Enter Teusaday Timetable', font = 'Roboto 10')
TeusdayEntry =ttk.Entry(master=SignUp)
Wednesday = ttk.Label(master=SignUp,text='Enter Wednesday Timetable', font = 'Roboto 10')
WednesdayEntry =ttk.Entry(master=SignUp)
Thursday = ttk.Label(master=SignUp,text='Enter Thursday Timetable', font = 'Roboto 10')
ThursdayEntry =ttk.Entry(master=SignUp)
Friday = ttk.Label(master=SignUp,text='Enter Friday Timetable', font = 'Roboto 10')
FridayEntry =ttk.Entry(master=SignUp)

SignUpPasswordLabel = ttk.Label(master=SignUp,text='Please Enter your Password', font = 'Roboto 10')
SignUpPasswordEntry = ttk.Entry(master=SignUp,show="*")
SignUpComplete = ttk.Button(master=SignUp,text='Submit',command=beginsignup,style = 'Submit.TButton')
Login_Return = ttk.Button(master = SignUp, text= 'Back to Login', command = signup_to_login, style = 'Standard.TButton')

#It now creates the tkinter widgets for the settings page in the Profile frame
ProfileLabel = ttk.Label(master = window, text = 'Profile', font = 'Roboto 20')
SettingsFrame = ttk.Frame(master = window)

UserEmailLabel = ttk.Label(master = SettingsFrame, text = 'Email', font = 'Roboto 12')
UserEmailEntry = ttk.Entry(master= SettingsFrame)
UpdateEmail = ttk.Button(master = SettingsFrame, text = 'Update', style = 'Submit.TButton', command = Update_Email)

UserNameLabel = ttk.Label(master = SettingsFrame, text = 'Name', font = 'Roboto 12')
Name_Entry = ttk.Entry(master=SettingsFrame)
Name_Update = ttk.Button(master=SettingsFrame, text  = 'Update', style = 'Submit.TButton', command = update_name)

User_Subject_Label = ttk.Label(master = SettingsFrame, text = 'Subject', font = 'Roboto 12')
SubjectsBox2 = ttk.Combobox(master=SettingsFrame)
SubjectsBox2['values'] = subjects
Subject_Update = ttk.Button(master = SettingsFrame, text = 'Update', style = 'Submit.TButton', command = update_subject )

Update_Year_Label = ttk.Label(master = SettingsFrame, text = 'Year Assigned', font = 'Roboto 12')
Year12_Update = tk.IntVar(value=0)
Year13_Update = tk.IntVar(value=0)
Year11_Update = tk.IntVar(value= 0)
Year10_Update = tk.IntVar(value= 0)
Year12_Update_Box = ttk.Checkbutton(master=SettingsFrame, text='Year 12', variable=Year12_Update)
Year13_Update_Box = ttk.Checkbutton(master=SettingsFrame, text='Year 13', variable=Year13_Update)
Year11_Update_Box = ttk.Checkbutton(master=SettingsFrame, text='Year 11', variable=Year11_Update)
Year10_Update_Box = ttk.Checkbutton(master=SettingsFrame, text='Year 10', variable=Year10_Update)
Year_Update = ttk.Button(master= SettingsFrame, text = 'Update', style = 'Submit.TButton', command = update_year )

UpdatePasswordLabel = ttk.Label(master=SettingsFrame,text='Would you like to update password', font = 'Roboto 12')
InitalPasswordLabel = ttk.Label(master=SettingsFrame,text='Enter your current password', font = 'Roboto 12')
Password = tk.StringVar()
InitalPasswordEntry = ttk.Entry(master=SettingsFrame,textvariable=Password,show="*")
InitalPasswordButton = ttk.Button(master=SettingsFrame, text='Submit', command=lambda: CheckPassword(Password.get().strip()))
NewPasswordLabel = ttk.Label(master=SettingsFrame,text='Enter your new password', font = 'Roboto 12')
NewPasswordEntry = ttk.Entry(master=SettingsFrame,show="*")
NewPasswordSumbit = ttk.Button(master=SettingsFrame, text='Submit', command=lambda: updatepassword(current_teacher.emailid, NewPasswordEntry.get().strip()))

#The widgets for the siderbar are now created
sidebar_frame = ttk.Frame(master=window, width=200, style = 'Sidebar.TFrame')
homebutton = ttk.Button(master=sidebar_frame,text='Home', style = 'SidebarButton.TButton',command=to_home)
button1 = ttk.Button(master=sidebar_frame, text='Attendance', style = 'SidebarButton.TButton' ,command=to_attendance)
button2 = ttk.Button(master=sidebar_frame, text='Analysis System',style = 'SidebarButton.TButton',command=to_analysis)
button3 = ttk.Button(master=sidebar_frame,text='Finder System',style = 'SidebarButton.TButton',command=to_finder)
button4 = ttk.Button(master=sidebar_frame,text='Settings',style = 'SidebarButton.TButton',command=to_settings)

#It now creates the widgets to be used in the home page inclurding the timetable display and timetable update widgets
welcometitle = ttk.Label(master = window, font= 'Roboto 32')
Timetable_Frame = ttk.Frame(master=window)
TimetableTitle = ttk.Label(master=Timetable_Frame, text='Today\'s Timetable', font='Roboto 24')

Timetable_Display = ttk.Treeview(master=Timetable_Frame, columns=('Time', 'Lesson', 'Status','Year Group'), style="Custom.Treeview", show = 'headings')
Timetable_Display.heading('Time', text = 'Lesson Start Time')
Timetable_Display.heading('Lesson', text = 'Lesson')
Timetable_Display.heading('Status', text = 'Status')
Timetable_Display.heading('Year Group', text = 'Year Group')
Timetable_Display.column('Time', width = 300, anchor = 'center')
Timetable_Display.column('Lesson', width = 250, anchor = 'center')
Timetable_Display.column('Status', width = 250, anchor = 'center')
Timetable_Display.column('Year Group', width = 250, anchor ='center')
Timetable_Display.bind('<ButtonRelease-1>', timetable_update_entry)

Timetable_Update_Frame = ttk.Frame(master=window)
Timetable_Update_Label = ttk.Label(master = Timetable_Update_Frame,text = 'Selected Lesson', font = 'Roboto 14')
Timetable_Subject_Update_Label = ttk.Label(master = Timetable_Update_Frame, text = 'Subject of Lesson:')
Timetable_Update_Subject = ttk.Entry(master = Timetable_Update_Frame)
Timetable_Year_Update_Label = ttk.Label(master = Timetable_Update_Frame, text = 'Year Group of Lesson:')
Timetable_Update_Year = ttk.Entry(master = Timetable_Update_Frame)


Lessons = ['Lesson 1','Lesson 2','Lesson 3','Lesson 4','Lesson 5','Lesson 6','Lesson 7','Lesson 8']

#The Attendance Display treeview is now also established
AttendanceDisplay = ttk.Treeview(master=window,columns=('Attendance','ID','Name','Year'),show='headings', style = 'Custom.Treeview')
AttendanceDisplay.heading('Attendance', text='Attendance')
AttendanceDisplay.heading('ID', text='Email ID')
AttendanceDisplay.heading('Name', text='Student Name')
AttendanceDisplay.heading('Year', text='Year Group')
AttendanceDisplay.column('Attendance', width=250, anchor='center')
AttendanceDisplay.column('ID', width=200, anchor='center')
AttendanceDisplay.column('Name', width=250, anchor='center')
AttendanceDisplay.column('Year', width=250, anchor='center')
AttendanceDisplay.bind('<ButtonRelease-1>', Attendance_Display_Begin)




#The widgets to be used in the analysis function are also created
AnalysisTitle = ttk.Label(master=window,text="Welcome to the Analysis System", font = 'Roboto 32')
AnalysisFrame = ttk.Frame(master=window)
DateTitle = ttk.Label(master=AnalysisFrame,text='Enter the date of the lesson you wish to analyze' ,font = 'Roboto 14')
calendar = ttk.DateEntry(master=AnalysisFrame, bootstyle = 'info')
LessonTitle = ttk.Label(master=AnalysisFrame,text='Which lesson was it on that day' , font = 'Roboto 14')
AnalysisLessonChoice = tk.StringVar()
AnalysisLesson = ttk.Combobox(master=AnalysisFrame,textvariable = AnalysisLessonChoice)
AnalysisLesson.configure(values=Lessons)
AnalysisButton = ttk.Button(master=AnalysisFrame,text='Begin Analysis',command=analysis, style = 'Submit.TButton')

SpecificAnalysisTitle = ttk.Label(master = AnalysisFrame, text = 'System belows allows Analysis of a student\'s specific records with a specific teacher', font = 'Roboto 14')
StudentTitle = ttk.Label(master=AnalysisFrame,text = 'Which Student do you wish to analyse', font = 'Roboto 14')
AnalysisStudentChoice = ttk.Entry(master=AnalysisFrame)
Specific_Analysis_Email = ttk.Label(master=AnalysisFrame, text = 'What is the teacher\'s Email', font = 'Roboto 14')
Specific_Analysis_Email_Entry = ttk.Entry(master=AnalysisFrame)
Analysis_Head_of_Year_Label = ttk.Button(master=window,text='Head of Year Analysis',command=HOY_Analysis, style =  'Standard.TButton')

StatsFrame = ttk.Frame(master = window)
PresentStudentsLabel = ttk.Label(master = StatsFrame,font = 'Roboto 18')
LateStudentsLabel = ttk.Label(master = StatsFrame,font = 'Roboto 18')
AbsentStudentsLabel = ttk.Label(master = StatsFrame,font = 'Roboto 18')
Average_Student_Lateness = ttk.Label(master = StatsFrame,font = 'Roboto 18')
Median_Student_Lateness = ttk.Label(master=StatsFrame,font = 'Roboto 18')

#The widgets for the head of year meny are also created
Head_of_Year_Menu = ttk.Frame(master=window)
WeekAnalysisButton = ttk.Button(master=Head_of_Year_Menu, text='Weekly Analysis', command=WeekAnalysisEntry , style =  'Standard.TButton')
SubjectAnalysisButton = ttk.Button(master=Head_of_Year_Menu, text='Subject Analysis', command=subjectanalysisentry, style =  'Standard.TButton')
StudentAnalysisButton = ttk.Button(master=Head_of_Year_Menu, text='Student Analysis', command=studentanalysisentry, style =  'Standard.TButton')


WeekLabel = ttk.Label(master=Head_of_Year_Menu, text='Enter the week you wish to analyze (start date:end date)', font = 'Roboto 18')
Startcalendar = ttk.DateEntry(master=Head_of_Year_Menu, bootstyle = 'info')
Endcalendar = ttk.DateEntry(master=Head_of_Year_Menu, bootstyle = 'info')


HOY_Student_Label = ttk.Label(master=Head_of_Year_Menu, text='Which Student\'s record would you like to check', font = 'Roboto 18')
HOY_Student_Code = ttk.Entry(master=Head_of_Year_Menu)

SubjectAnalysis_Label = ttk.Label(master=Head_of_Year_Menu, text='Which Subject would you like to Analyse', font = 'Roboto 18')
SubjectAnalysis_Entry = ttk.Entry(master= Head_of_Year_Menu)

#The widgets for the finder system are now also created
DisplayRecord = ttk.Label(master=window, font='Roboto 18')
PotentialNodes = ttk.Label(master = window, font='Roboto 18')
canvas_widget = None

#It now packs all the widgets for the sign up frame though these won't be seen as the sign up frame itself is not packed
SignUpTitle.grid(row=0, columnspan=2)
Email.grid(row=1, column=0, sticky='w', pady=5)
EmailsignupEntry.grid(row=1, column=1, sticky='w', pady=5)
name.grid(row=2, column=0, sticky='w', pady=5)
nameEntry.grid(row=2, column=1, sticky='w', pady=5)
subjectlabel.grid(row=3, column=0, sticky='w', pady=5)
SubjectsBox.grid(row=3, column=1, sticky='w', pady=5)
YearLabel.grid(row=4, column=0, sticky='w', pady=5)
year10button.grid(row=4, column=1, sticky='w', pady=5)
year11button.grid(row=4, column=2, sticky='w', pady=5)
year12.grid(row=5, column=1, sticky='w', pady=5)  
year13.grid(row=5, column=2, sticky='w', pady=5) 
RoleAssignedLabel.grid(row=6, column=0, sticky='w', pady=5)
Teacher.grid(row=6, column=1, sticky='w', pady=5)
Head_of_Year_Pick.grid(row=6, column=2, sticky='w', pady=5)
LeadingLabel.grid(row=7, column=0, sticky='w', pady=5)
LeadingEntry.grid(row=7, column=1, sticky='w', pady=5)
RoomLabel.grid(row=8, column=0, sticky='w', pady=5)
RoomEntry.grid(row=8, column=1, sticky='w', pady=5,padx = 5)
TimetableLabel.grid(row=9, column=0, columnspan=2, pady=5)
Monday.grid(row=10, column=0, sticky='w', pady=5)
MondayEntry.grid(row=10, column=1, sticky='w', pady=5)
Teusday.grid(row=11, column=0, sticky='w', pady=5)
TeusdayEntry.grid(row=11, column=1, sticky='w', pady=5)
Wednesday.grid(row=12, column=0, sticky='w', pady=5)
WednesdayEntry.grid(row=12, column=1, sticky='w', pady=5)
Thursday.grid(row=13, column=0, sticky='w', pady=5)
ThursdayEntry.grid(row=13, column=1, sticky='w', pady=5)
Friday.grid(row=14, column=0, sticky='w', pady=5)
FridayEntry.grid(row=14, column=1, sticky='w', pady=5)
SignUpPasswordLabel.grid(row=15, column=0, sticky='w', pady=5)
SignUpPasswordEntry.grid(row=15, column=1, sticky='w', pady=5)
SignUpComplete.grid(row=16, columnspan=2, pady=10) 
Login_Return.grid(row=16, column=2, sticky='w', pady=10) 



window.mainloop()
connection.close()
