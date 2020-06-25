"""
Name: Student Partition Optimization Tool for Schools (SPOTS)

Version: 1.0.0a1

Summary: Optimize a student partition (usually assigning each student to A/B/C/D) to facilitate physical distancing in classrooms

Description: State governments and public health agencies have begun recommending that schools implement "Physically Distanced Learning," with a student/teacher ratio of 10/1 or fewer in each classroom. At most schools, this will require rotating groups of students into the school building while other students stay home and learn remotely. This project aims to help schools assign students to an A/B/C/D group in a manner that allows physical distancing in as many classrooms as possible. 

Video Description: https://youtu.be/XJFvY4-FCSc

Author: Christopher Grattoni

Author-email: studentpartitionoptimizer@gmail.com 

License: GNU Affero General Public License v3.0 (GNU AGPLv3)

License-URL: https://www.gnu.org/licenses/agpl-3.0.en.html

Requires-Python: >= 3.8 (Feature from version 3.7+: dictionary order is guaranteed to be insertion order. Source: https://docs.python.org/3/library/stdtypes.html#dict) 

Project-URL: https://github.com/NFLtheorem/partitionoptimizer 
"""

# import statements: 
import random # used in the set_letter method of the Student class
import csv # used in students_from_csv method of IndividualPartition class
import time # use when benchmarking and setting an evaluation time limit:
            # start = time.perf_counter()
            # (do something)
            # end = time.perf_counter()
            # print("Benchmark result = " + str(end - start))
import warnings # used in run_loop() to remind users to close output reports
                # before running the algorithm a second time 

# parameters for main algorithm
NUMBER_OF_PARTITIONS = 4 # number of groups to partition students into (only 2 and 4 are implemented)
MUTATION_RATE = 0.015 # recommended range: between 0.01 and 0.05, current default = 0.015
POPULATION_SIZE = 200 # recommended range: between 100 and 1,000, current default = 200
NUMBER_OF_GENERATIONS = 100000 # recommended range: at least 10,000, current default = 100000
IO_DIRECTORY = "C:\\YOUR_DIRECTORY_HERE" # location of input .csv file, for example "C:\\Users\\jsmith\\Desktop\\"
INPUT_CSV_FILENAME = "example.csv" # filename of .csv file
TIME_LIMIT = 60*8 # time measured in minutes, current default = 480 min (8 hr)

# REQUEST FOR USERS
#
# As you experiment with the MUTATION_RATE, POPULATION_SIZE, and NUMBER_OF_GENERATIONS,
# you may happen upon a combination of values that optimizes more efficiently than the
# default settings in this program. If so, please share these values with me at 
# studentpartitionoptimizer@gmail.com so I can verify and make these the new defaults.

class Student:
    """
    A class used to store attributes about individual students, 
    where students are uniquely identified by an ID number
    
    Attributes
    ----------
    last_name : str
        the last name of the student (ex: Smith)
    middle_name : str
        the middle name of the student (ex: Jay)
    first_name : str
        the first name of the student (ex: John)
    id : str
        the unique ID number of the student (ex: 817281)
        (must be unique for each student)
    schedule : list of course objects
        the student's schedule as a list of course objects
    letter : str
        the assigned partition letter (default is A/B/C/D)
    number_of_partitions : int
        the number of partitions students are to be separated into (default value is 4)
            
    Methods
    -------
    
    None 
    
    """    
    
    def __init__(self, id): 
        """
        The constructor for the Student class 
        
        Parameters
        ----------
        id : str
            the ID number of the student (must be unique)
        """
        
        self.id = id
        self.schedule = [] # course objects will be appended onto this list
        self.last_name = None
        self.middle_name = None
        self.first_name = None
        self.letter = None
        self.number_of_partitions = None
    
class Course:
    """
    A class used to store attributes about individual courses, where 
    each course is uniquely identified by (room_number, period)
    
    Attributes
    ----------
    room_number : str
        the room the course is in (ex: 254)
    period : int
        the period the course is taking place (ex: 5)
    course_number_list : list
        a list of all course numbers running in this particular room 
        during this particular period (ex: ["M11701", "M11401"], ...)
    course_name_list : list
        a list of all courses running in this particular room during 
        this particular period (ex: ["Algebra I", "Pre-algebra"], ...)
    course_id_list : list
        a list of all unique course_ids in this particular room during 
        this particular period (ex: ["30121", "91811", ...]
    roster : list
        a list of student objects that represents the students taking 
        a course in this particular room during this particular period 
        (ex: [student_obj1, student obj2, ...]
        
    Methods
    -------
    
    None
    
    """
    
    def __init__(self, room_number, period):
        """
        The constructor for the Course class
        
        Parameters
        ----------
        room_number : str
            the room the course is in (ex: 254)
        period : int
            the period the course is taking place (ex: 5)

        """
        self.room_number = room_number
        self.period = period
        self.course_number_list = [] # course numbers will be appended here
        self.course_name_list = [] # names of courses will be appended here
        self.course_id_list = [] # course IDs will be appended here
        self.roster = [] # students on the course's roster will be appended here

class Schedule:
    """
    A class used to store detailed attributes about a school's schedule
    (courses, rosters, and A/B/C/D assignments for students)
    
    Attributes
    ----------

    number_of_partitions : int
        the number of partitions students are to be separated into 
        (default value is 4)
    student_list : list
        a list of tuples in the form (student_object, schedule_list) 
        student_object: an object representing a single student
        student_schedule: a list of course objects that the student 
        is enrolled in
    course_dict : dict
        key: a course object
        value: a course roster (a list of student objects enrolled 
        in the course)
            
    Methods
    -------
    students_from_csv(file_location)
        populates student_list and course_dict from a .csv file
    load_partition(letter_list)
        load a list of letter assignments into the letter attribute
        for each student object in Schedule.student_list
    write_student_assignments()
        write a report of final student assignments in .csv format
    write_course_analysis()
        write an report of the letter breakdown in each classroom 
        as a .csv file
    fitness_score()
        evaluates the fitness of the schedule, where the specific 
        fitness function is based on the number of partitions 
        students are divided into (if number_of_partitions is set
        to any values other than 2 or 4, this function must be updated)
    verify_student_schedule(student_id)
        get a student's course schedule from the student's ID number
    verify_roster(room, period)
        get a course's roster given the room and period the course 
        is taking place
    """
    
    def __init__(self, number_of_partitions = 4):
        """
        The constructor for the Schedule class
        
        Parameters
        ----------
        number_of_partitions : int
            the number of partitions students are to be separated into 
            (default value is 4)
        """
        self.number_of_partitions = number_of_partitions
        
        # changed student_list to a list so users using old versions of Python (< 3.7) 
        # do not run into issues with iterating over a dictionary in a deterministic order
        # 
        # Python 3.7: dictionary order guaranteed to be in insertion order:
        # https://docs.python.org/3/library/stdtypes.html#dict, dictionary order 
        #
        # before Python 3.7, dictionary order was not guaranteed
        #
        self.student_list = []
        self.course_dict = {}

    def students_from_csv(self, file_location):
        """
        A method to populate student_list and course_dict from a .csv file
        
        The .csv file should have an entry for each student course enrollment.
        For example, if John Smith is taking 7 classes, then John Smith should
        have 7 rows in the .csv file:
        
        LAST,FIRST,MIDDLE,STUDENT_ID,COURSE_NUMBER,COURSE_NAME,COURSE_ID,ROOM_NUMBER,PERIOD
        John,Smith,William,000281871,Math435-01,ALGEBRA 2/TRIG,299381878,ROOM 255, PERIOD 1
        John,Smith,William,000281871,Eng402-01,ADV BRITISH LIT,345342243,ROOM 211, PERIOD 2
        John,Smith,William,000281871,Hist424-01,AP WORLD HIST,5011222439,ROOM 166, PERIOD 3
        John,Smith,William,000281871,Chem419-01,AP CHEMISTRY,54441133238,ROOM 200, PERIOD 5
        John,Smith,William,000281871,Band300-01,MARCHING BAND,4032191878,ROOM 003, PERIOD 6
        John,Smith,William,000281871,Germ461-01,AP GERMAN LANG,198243981,ROOM 214, PERIOD 7
        John,Smith,William,000281871,Gym400-01,ADVENTURE EDUCATION,23423,ROOM GYM, PERIOD 8
        
        This algorithm can be modified to accommodate additional attributes about students or
        courses that can be added to the .csv file. For example, it is possible to add a row
        for the teacher of each course. It is also possible to modify the algorithm to run with
        fewer rows. The only rows that cannot be deleted are STUDENT_ID, ROOM_NUMBER, and PERIOD. 
        This is because STUDENT_ID is the unique identifier for each student and the tuple
        (ROOM_NUMBER, PERIOD) is the unique identifier for each course. 
        
        A .csv file in the above form is easy to generate in Infinite Campus.
        
        Parameters
        ----------
        csv_file_location : str
            the file path of a .csv file with student enrollment data, for 
            example C:\\Users\\jsmith\\student_data.csv
        """
        
        # import the .csv:
        with open(file_location, mode='r') as infile:
            # each course is uniquely identified by the tuple (room, period)
            # temp_course_dict is a dictionary with the following:
            # key: (room, period)
            # value: associated Course object
            temp_course_dict = {}
            
            # each student is uniquely identified by their ID number
            # temp_student_dict is a dictionary with the following:
            # key: ID number
            # value: associated Student object
            temp_student_dict = {}
            
            # read the .csv file            
            # note: reader method ended up being faster than csv.DictReader objects
            # https://courses.cs.washington.edu/courses/cse140/13wi/csv-parsing.html
            reader = csv.reader(infile)
            
            # skip the first row since the first row contains headers
            next(reader) 
            
            # description of the columns in the .csv file:
            for row in reader:
                # row[0] : LAST NAME (ex: Smith)
                last_name = row[0]
                
                # row[1] : FIRST NAME (ex: John)
                first_name = row[1]
                
                # row[2] : MIDDLE NAME (ex: Jacob)
                middle_name = row[2]

                # row[3] : STUDENT ID (ex: 123456)
                student_id = row[3]

                # row[4] : COURSE NUMBER (ex: M11701)
                course_number = row[4]

                # IMPORTANT: If you are only considering first semester courses,
                # check if the course number ends in a '1'. If it does not, then
                # continue to the next iteration of the loop
                
                #if course_number[-1] != '1':
                #    continue
                
                # row[5] : COURSE NAME (ex: Algebra 1)
                course_name = row[5]

                # row[6] : COURSE ID (ex: 801900)
                course_id = row[6]

                # row[7] : ROOM NUMBER (ex: Room 254)
                room_number = row[7]
                
                # row[8] : PERIOD (ex: 5)
                period = row[8]

                # first, set current_student to an appropriate Student object:
                
                # check if student_id is NOT in our temp_student_dict
                if student_id not in temp_student_dict:
                    # if the student is not in temp_student_dict,
                    # then instantiate a Student object and assign 
                    # it to current_student:
                    current_student = Student(student_id)
                    current_student.last_name = row[0]
                    current_student.middle_name = row[2]
                    current_student.first_name = row[1]

                    # next, add to temp_student_dict using:
                    # key: student_id 
                    # value: Student object
                    temp_student_dict[student_id] = current_student                    
                    
                # otherwise, student_id **is** in our temp_student_dict:
                else:
                    # access this Student object and assign it to current_student:
                    current_student = temp_student_dict[student_id]

                # now current_student is assigned, but the Student object
                # does not yet have its associated Course object appended
                # to Student.schedule
                
                # next, set current_course to an appropriate Course object
                
                # check if the course the student is taking is NOT in our temp_course_dict:
                if (room_number, period) not in temp_course_dict:
                    # if the course is not in temp_course_dict,
                    # then instantiate a course object:
                    current_course = Course(room_number, period)
                    current_course.course_number_list.append(course_number)
                    current_course.course_name_list.append(course_name)
                    current_course.course_id_list.append(course_id)
                        
                    # next, add to temp_course_dict using:
                    # key: (room_number, period) 
                    # value: Course object
                    temp_course_dict[(room_number, period)] = current_course
                
                # if (room_number, period) **is** in our temp_course_dict, then 
                # the Course object already exists, so we just need the following: 
                else:
                    # access this Course object and assign it to current_course:
                    current_course = temp_course_dict[(room_number, period)]
                                        
                    # append any newly encountered course numbers/names/ids to the
                    # appropriate lists:
                    if course_number not in current_course.course_number_list:
                        current_course.course_number_list.append(course_number)
                    if course_name not in current_course.course_name_list:
                        current_course.course_name_list.append(course_name)
                    if course_id not in current_course.course_id_list:
                        current_course.course_id_list.append(course_id)
                    
                # now current_course is assigned, but the Course object
                # does not yet have its associated Student object appended
                # to Course.roster
                current_course.roster.append(current_student)
                
                # similarly, current_student is assigned, but the Student object
                # does not yet have its associated Course object appended
                # to Student.schedule:
                current_student.schedule.append(current_course)
 
            # now that temp_course_dict has a unique key for each 
            # course, we can iterate over the dictionary to populate
            # our course_dict:
            # key: a Course object
            #       (a class being held in a particular (room, period))
            # value: a list of all Student objects in the course 
            #       (aka: a roster)            
            for key in temp_course_dict:
                new_key = temp_course_dict[key]
                new_value = new_key.roster
                self.course_dict[new_key] = new_value

            # now that temp_student_dict has a unique key for each 
            # student, we can iterate over the dictionary to populate
            # our student_list with tuples in the form (student, schedule):
            # student: a Student object 
            #       (a student at the school)
            # schedule: a list of Course objects the student is taking 
            #       (aka: a course schedule)    
            
            for key in temp_student_dict:
                student_obj = temp_student_dict[key]
                schedule = student_obj.schedule
                self.student_list.append((student_obj, schedule))

    def load_partition(self, letter_list):
        """
        A method to load a list of letters into the letter attribute for 
        each student object in Schedule.student_list
        
        For example, suppose letter_list = ["A", "B", "A", "D"]. Also suppose that 
        student_list = [student_obj1, student_obj2, student_obj3, student_obj4].
        Then Schedule.load_partition(letter_list) would lead to the following result:
        
        student_obj1.letter = "A"
        student_obj2.letter = "B"
        student_obj3.letter = "A"
        student_obj4.letter = "D"
        
        This method is used when we need to evaluate the fitness of a newly-generated partition.
        
        Parameters
        ----------
        letter_list : list
            a list of letter assignments for each student at the school, for example a school with
            four students could have ["A", "B", "A", "D"]
        """
        number_of_partitions = self.number_of_partitions
        
        for i in range(len(letter_list)):
            letter = letter_list[i]
            student = self.student_list[i][0]
            student.letter = letter

    def write_student_assignments(self):
        """
        A method to write a report of final student assignments in .csv format
        
        For example:
        id number,last name,first name,middle name,letter
        091834273,Smithfield,Jonathan,Christopher,A
        023421760,Thomasville,Abigail,Heather May,B        
        
        Parameters
        ----------
        None
        """
        # the file name and location for the student assignment report:
        output_file = IO_DIRECTORY + 'student_assignments.csv' 
        
        with open(output_file, 'w') as file:
            # write the headers of the .csv
            headers = "id,last name,first name,middle name,letter"
            file.write(headers)
            file.write("\n")   
            
            # write a line in the .csv for each student in student_list:
            for tuple in self.student_list: 
                student_obj = tuple[0]
                current_id = student_obj.id
                current_last = student_obj.last_name
                current_first = student_obj.first_name
                current_middle = student_obj.middle_name
                current_letter = student_obj.letter
                
                line = current_id + "," + current_last + "," + current_first + "," + current_middle + "," + current_letter
                
                file.write(line)
                
                file.write("\n")

    def write_course_analysis(self):
        """
        A method to write an report of the letter breakdown in each classroom
        as a .csv file (only implemented for A/B and A/B/C/D partitions)
        
        Summary of .csv headers: 
        room,period,course_number_list,total_students,A_count,B_count,C_count,D_count,A_ratio,B_ratio,C_ratio,D_ration,max_deviation,in compliance?
        
        Example data #1:
        254,5,[M11701, M11401], 24, 6, 6, 6, 6, 0.25, 0.25, 0.25, 0.25, 0, Yes
        
        This example says that the class in Rm 254 during 5th hour has
        24 students, with 6 A's, 6 B's, 6 C's, 6 D's, each comprising 25% of the
        total course roster. This course is in compliance with physical distancing 
        requirements since each A/B/C/D subgroup is 9 or fewer students.
        
        Example data #2:
        201,6,[E10101], 32, 10, 6, 8, 8, 0.3125, 0.1875, 0.25, 0.25, 0.0625, No
        
        This example says that the class in Rm 201 during 6th hour has
        32 students, with 10 A's, 6 B's, 6 C's, 6 D's. The A's comprise
        31.25% of the class, the B's are 18.75% of the class, and the 
        C's/D's are each 25% of the class. The max deviation is 0.0625, 
        which is found by 0.3125 - 0.25 = 0.0625. This course is NOT in 
        compliance with physical distancing requirements since the A-group
        exceeds 9 students. 
                
        Parameters
        ----------
        None
        """
        # the file name and location for the course analysis report:
        output_file = IO_DIRECTORY + 'course_analysis.csv' 
        
        # if number_of_partitions is not 2 or 4, you will have to 
        # implement your own analysis
        if self.number_of_partitions != 2 and self.number_of_partitions != 4:
            print("In order to choose something other than an AB or ABCD partition, you must write your own final analysis")    
            raise NotImplementedError        
        
        else:
            with open(output_file, 'w') as file:
                # a list in the form ["A", "B", "C", "D", ...], 
                # where the length of the list is based on the
                # size of the partition, this will either be
                # ["A", "B"] or ["A", "B", "C", "D"] with the
                # current implementation 
                possible_letter_list = [chr(i + 65) for i in range(0, self.number_of_partitions)]
            
                # concatenate the header row for the .csv file:
                headers = "room,period,section list,total students"

                for letter in possible_letter_list:
                    headers += "," + letter + " count"

                for letter in possible_letter_list:
                    headers += "," + letter + " ratio"

                headers += ",max deviation,in compliance?"
                
                # write the headers to the .csv file:
                file.write(headers)
                file.write("\n")  
                
                # for each course at the school:
                for course in self.course_dict:
                    # concatenate a row of data about the course, as a
                    # string where each value is delimited by a comma:
                    line = course.room_number # room number for the course
                    line += ","
                    line += course.period # period the course is running
                    line += ","
                    line += '"' + str(course.course_number_list) +'"' # a list of all courses in this (room, period)
                    line += ","
                    
                    roster = self.course_dict[course] # a roster of students taking the course
                    total_students = len(roster) # the number of students on the roster for this course
                    
                    line += str(total_students)
                    line += ","
                    
                    # prepare to count each letter, where counts = [0,0] for A/B 
                    # and counts = [0,0,0,0] for A/B/C/D:
                    counts = [0 for i in range(0, self.number_of_partitions)] 
            
                    # for each student on the roster:
                    for student in roster:
                        # use the student's assigned letter to find the correct
                        # index in [0,0,0,0] to increment
                        index = possible_letter_list.index(student.letter) 
                    
                        # and then increment it:
                        counts[index] += 1 # 
                    
                    # concatenate these values onto the row, delimited by commas:
                    for count in counts:
                        line += str(count)
                        line += ","
                    
                    # calculate the ratio for each letter:
                    ratios = [count/total_students for count in counts]
                    
                    # concatenate the ratios onto the row, delimited by commas:
                    for ratio in ratios:
                        line += str(ratio)
                        line += ","
                    
                    # max_deviation is the largest ratio minus the value 
                    # that would occur for an even distribution between
                    # each letter:
                    max_deviation = max(ratios) - 1/len(ratios)
                    
                    # concatenate max_deviation onto the row, delimited by a comma:                    
                    line += str(max_deviation)
                    line += ","
                    
                    # next, we determine if the course is "In Compliance" with 
                    # physical distancing rules
                    if self.number_of_partitions == 2:
                        # for an A/B partition, we say that a course is
                        # "In Compliance" if there are no more than 15 
                        # students in either group
                        if counts[0] <= 15 and counts[1] <= 15:
                            line += "Yes" 
                        else:
                            line += "No"
                        
                    elif self.number_of_partitions == 4:
                        a_count = counts[0]
                        b_count = counts[1]
                        c_count = counts[2]
                        d_count = counts[3]
                        
                        # for an A/B/C/D partition, we say that a course is
                        # "In Compliance" if there are no more than 9 students
                        # in any of the four groups:
                        check_individually = (a_count <= 9 and b_count <= 9 and c_count <= 9 and d_count <= 9)
                        
                        # we also require that the (A+B) and (C+D) combined 
                        # groups are no more than 15 students:                        
                        check_pairs = (a_count + b_count <= 15 and c_count + d_count <= 15)
                        
                        # if the course passes both tests, it is "In Compliance"
                        if check_individually and check_pairs:
                            line += "Yes"
                        # if it fails either test, it is "Out of Compliance"
                        else:
                            line += "No"
                    
                    # write the concatenated string to the .csv file
                    file.write(line)
                    # write a line break
                    file.write("\n")

    def fitness_score(self):
        """
        A method to evaluate the fitness of a particular partition of 
        students based on how that partition interacts with the 
        school's schedule (courses and the rosters of those courses)
        
        fitness score maximum value: this is scaled to have have a 
        maximum score of 100, which can only be achieved when all 
        courses at the school are classified as "In Compliance"
        
        fitness score minimum value: penalties are applied to "Out of 
        Compliance" courses whose distribution of A/B/C/D strays too 
        far from an even distribution, so early generations are likely
        to have a negative fitness score because of accumulating too
        many penalties
        
        Note: this function is only implemented for 
        number_of_partitions = 2 and = 4
        
        Note: this function should be modified if a school has a different
        set of requirements to classify a course as "In Compliance."  
        
        REQUEST FOR USERS: If you experiment with the logic in this fitness 
        function and happen upon a modification that leads to better (or faster)
        results, please share with me at studentpartitionoptimizer@gmail.com 
        so I can verify and incorporate below.
                
        Parameters
        ----------
        None
        """
        # a floating point number, the most important value that fitness_function
        # tracks 
        #
        # we are trying to maximize weighted_fitness_score
        #
        # max score: 100 (achieved if all courses are classified as "In Compliance")
        # 
        # min score: a negative number (penalties are applied depending 
        # on how far the course is from having an even distribution of 
        # students from each letter group)
        weighted_fitness_score = 0 
        
        # incremented whenever a course is penalized, a raw count of the number
        # of penalties applied (useful for debugging purposes)
        penalty_count = 0
        
        # a count of the number of courses that are "In Compliance" 
        good_score = 0
        
        # a raw count of any cases that were not counted by the previous scores 
        # (useful for debugging purposes)
        other_score = 0
        
        # the number of courses at the school
        number_of_courses = len(self.course_dict)

        # fitness function for an A/B partition:
        if self.number_of_partitions == 2:
            # for each course:
            for course in self.course_dict:
                # get the course's roster:
                roster = self.course_dict[course]
                
                a_count = 0
                b_count = 0
            
                # count the A's and B's on the course roster:
                for student in roster:
                    letter = student.letter
                    if letter == "A":
                        a_count += 1
                    elif letter == "B":
                        b_count += 1
                
                # the total number of students in the course
                total = len(roster)
                
                # relative percentage of A's and B's:
                a_percent = a_count/total
                b_percent = b_count/total
                
                # calculate the deviation from a 50/50 split
                # between A's and B's: 
                percent_difference = abs(a_percent - b_percent)

                # we are classifying a course as "In Compliance"
                # if it has no more than 15 A's and 15 B's:
                if a_count <= 15 and b_count <= 15:
                    # increment the raw "In Compliance" score:
                    good_score += 1 
                    # increment the weighted_fitness_score:
                    weighted_fitness_score += 1/total 
                # otherwise, apply a penalty based on how far the course
                # deviates from a 50/50 split betwen A's and B':
                elif a_count <= 15 and b_count > 15:
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                elif a_count > 15 and b_count <= 15:
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                # if we make it here, a_count and b_count are 
                # both above 15, so no partition can ever get 
                # a_count <= 15 and b_count <= 15, instead we try
                # to make sure that the relative ratio between A's 
                # and B's is better than a 55/45 split 
                elif a_percent > 0.55:
                    # penalize if the section deviates from a 
                    # 55/45 split between A/B
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                elif b_percent > 0.55:
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                else:
                    # a raw count of any cases that were not 
                    # counted by the previous statements
                    other_score += 1
        
        # fitness function for an A/B/C/D partition:
        elif self.number_of_partitions == 4:
            # for each course:
            for course in self.course_dict:
                # get the course's roster:
                roster = self.course_dict[course]
                
                a_count = 0
                b_count = 0
                c_count = 0
                d_count = 0
                
                # count the A's/B's/C's/D's on the roster:
                for student in roster:
                    letter = student.letter
                    if letter == "A":
                        a_count += 1
                    elif letter == "B":
                        b_count += 1
                    elif letter == "C":
                        c_count += 1
                    elif letter == "D":
                        d_count += 1
                
                # the total number of students on the roster:
                total = len(roster)
                
                # relative percentage of A's/B's/C's/D's:
                a_percent = a_count/total
                b_percent = b_count/total
                c_percent = c_count/total
                d_percent = d_count/total
                
                # check if there are no more than 9 students of any letter:
                check_individually = (a_count <= 9 and b_count <= 9 and c_count <= 9 and d_count <= 9)
                
                # check if the (A+B) count and (C+D) count are each less
                # than 15 students:
                check_pairs = (a_count + b_count <= 15 and c_count + d_count <= 15)
                
                # we classify a course as "In Compliance" if there
                # are no more than 9 students of any letter, and if
                # the (A+B) count and the (C+D) are each less than or
                # equal to 15
                if check_individually and check_pairs:
                    # increment the raw "In Compliance" score:
                    good_score += 1
                    # increment the weighted_fitness_score:
                    weighted_fitness_score += 1/total

                # otherwise, start subtracting from the weighted_fitness_score, 
                # where penalties are applied based on how far the course deviates
                # from an even distribution of A/B/C/D:
                else: 
                    # subtract from weighted_fitness_score if a_percent + b_percent
                    # is over 55% of the roster:
                    
                    # default value of pairwise_multiplier = 0.5
                    #
                    # change this depending on what you want to emphasize in the search:
                    #
                    # increase to emphasize an even distribution between the (A+B) and
                    # (C+D) groups (work towards a 50/50 split between these groups)
                    # 
                    # decrease to emphasize "In Compliance" courses
                    pairwise_multiplier = 0.5
                    
                    # default value = 0.25
                    #
                    # change this depending on what you want to emphasize in the search:
                    #
                    # increase to emphasize an even distribution between the A/B/C/D groups
                    #
                    # decrease to emphasize "In Compliance" courses                    
                    individual_multiplier = 0.25
                   
                    if a_percent + b_percent > 0.55:
                        # see note above about pairwise_multiplier
                        weighted_fitness_score -= pairwise_multiplier*(a_percent + b_percent - 0.5)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if c_percent + d_percent
                    # is over 55% of the roster:
                    if c_percent + d_percent > 0.55:
                        # see note above about pairwise_multiplier
                        weighted_fitness_score -= pairwise_multiplier*(c_percent + d_percent - 0.5)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if a_percent exceeds 30% of the roster:
                    if a_percent > 0.3:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(a_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if b_percent exceeds 30% of the roster:
                    if b_percent > 0.3:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(b_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if c_percent exceeds 30% of the roster:
                    if c_percent > 0.3:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(c_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if d_percent exceeds 30% of the roster:
                    if d_percent > 0.3:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(d_percent - 0.25)
                        penalty_count += 1
                    # an "Out of Compliance" section for which no penalty was applied:                    
                    if (a_percent <= 0.3 and b_percent <= 0.3 and c_percent <= 0.3 and d_percent <= 0.3) and (a_percent + b_percent <= 0.55 and (c_percent + d_percent) <= 0.55):
                        other_score += 1
        
        else: 
            print("In order to choose something other than an AB or ABCD partition, you must add your own fitness function")    
            raise NotImplementedError
        
        # return the following tuple, where weighted_fitness_score is the value 
        # we are trying to minimize and good_score is the number of courses that 
        # are in compliance
        return weighted_fitness_score, penalty_count, good_score, other_score, number_of_courses

    def verify_student_schedule(self, student_id):
        """
        A method for getting a student's course schedule from the student's
        ID number (this method exists for debug/data verification purposes)
        
        input: the student's id (str)
        output: a list in the form [student name, [(room, period) for each course]]
        
        Note: this could be replaced using __repr__ 
        Source: https://dbader.org/blog/python-repr-vs-str
        
        Parameters
        ----------
        student_id : str
            a student's ID number
        """

        for tuple in self.student_list:
            student = tuple[0]
            if student.id == student_id:
                student_letter_name = "Group: " + student.letter + ", Name: " + student.last_name + ", " + student.first_name
                current_classes = tuple[1]
        
        return [student_letter_name, [(course.room_number, course.period) for course in current_classes]]
    
    def verify_roster(self, room, period):
        """
        A method for getting a course's roster given the room and period 
        the course is taking place
        
        input: room (str) and period (str) of course
        output: a list of names for each student on the roster 
        
        Note: this could be replaced using __repr__ 
        Source: https://dbader.org/blog/python-repr-vs-str
        
        Parameters
        ----------
        room : str
            the room where the course is taking place
        period : str
            the period where the course is taking place
        """
        for course in self.course_dict:
            if course.room_number == room and course.period == period:
                current_roster = self.course_dict[course]
        
        return [(room, period), [("Group: " + student.letter + ", Name: " + student.last_name + ", " + student.first_name) for student in current_roster]]

class IndividualPartition(Schedule):
    """
    A class used to store an individual partition of the student
    body as an ordered list of letter assignments
    
    Ex: ["A", "A", "C", "B", "D", "A", ...]
    
    Attributes
    ----------
    schedule_obj: Schedule object
        inherited from the schedule class
    
    number_of_partitions: int
        inherited from the schedule class
        
    partition : list
        an individual partition of the student body stored as a 
        list of letters, ex: ["A", "A", "C", "B", "D", "A", ...]
        
    fitness: tuple
        a tuple representing the fitness of the partition in the form:
        (weighted_fitness_score, penalty_count, good_score, other_score, number_of_courses)
        
    
    Methods
    -------
    return_fitness(number_of_partitions)
        applies the partition to the Schedule object, and then 
        uses the Schedule.evaluate_fitness() method to get
        the fitness of partition_list

    generate_partition()
        generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
    """
    
    def __init__(self, schedule_obj):
        """
        The constructor for the IndividualPartition class
        
        Parameters
        ----------
        schedule_obj: Schedule object
            inherited from the schedule class
        """
        self.schedule_obj = schedule_obj
        self.number_of_partitions = schedule_obj.number_of_partitions
        self.partition = None
        self.fitness = None

    def generate_partition(self):
        """
        A method to generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
        
        Parameters
        ----------
        None
        
        """        
        
        # use the number_of_partitions to determine which letters to use
        letter_list = [chr(i + 65) for i in range(0, self.number_of_partitions)]
        
        student_partition_list = []
    
        # use number_of_students to determine how many letters are needed
        number_of_students = len(self.schedule_obj.student_list)
        
        # populate the list, ex: ["A", "A", "C", "B", "D", "A", ...] 
        for _ in range(number_of_students):
            letter = random.choice(letter_list)
            student_partition_list.append(letter)        
        
        # store the list in the self.partition attribute
        self.partition = student_partition_list

        return self.partition

    def return_fitness(self):
        """
        A method that loads the current partition into the Schedule object
        and returns the fitness score of that partition
        
        Parameters
        ----------
        None
        
        """
        self.schedule_obj.load_partition(self.partition)        
        self.fitness = self.schedule_obj.fitness_score()
        return self.schedule_obj.fitness_score()
        
class Population(IndividualPartition):
    """
    A class used to store a population of partitions (numerous IndividualPartition objects)
    
    Attributes
    ----------
    individual_partition_obj : IndividualPartition object
        inherited from the IndividualPartition class
    
    population_size : int
        the number of individuals in the population
        
    population : list
        a list of IndividualPartition objects that represent the population 
        (ex: [partition1, partition2, ...]
    
    sorted_scored_population : list
        a list of tuples in the form [(score1, partition1), (score2, partition2), ...] 
        that is sorted by fitness score in descending order (so score1 is highest)
        
    number_of_partitions: int
        inherited from the IndividualSchedule class
    
    Methods
    -------
    generate_individual()
        generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
    populate():
        generate a population of N individuals (random partitions), where N is 
        self.number_of_partitions and each individual is appended to the list 
        at self.population
    population_fitness()
        assess the fitness of each individual in the population, stored in 
        the attribute self.sorted_scored_population as a list in the form
        [(score1, population1), (score2, population2), ...] where the 
        scores are listed in descending order 
    """
    
    def __init__(self, individual_partition_obj, population_size):
        """
        Parameters
        ----------
        individual_partition_obj : IndividualPartition object
            inherited from the IndividualPartition class
    
        population_size : int
            the number of individuals in the population            
        
        """
        self.individual_partition_obj = individual_partition_obj
        self.population_size = population_size
        self.population = []
        self.sorted_scored_population = []
        self.number_of_partitions = individual_partition_obj.number_of_partitions

    def generate_individual(self):
        """
        A method to generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
        
        Parameters
        ----------
        None
        """
        
        return self.individual_partition_obj.generate_partition()

    def populate(self):
        """
        A method to generate a population of N individuals (random partitions),
        where N is self.number_of_partitions and each individual is appended
        to the list at self.population
        
        Parameters
        ----------
        None
        """
        
        for _ in range(self.population_size):
            individual = self.individual_partition_obj.generate_partition()
            self.population.append(individual)

    def population_fitness(self):
        """
        A method to assess the fitness of each individual in the population, 
        stored in the attribute self.sorted_scored_population as a list in the form
        [(score1, population1), (score2, population2), ...] where the 
        scores are listed in descending order 
        
        Parameters
        ----------
        None
        """
        for individual in self.population:
            self.individual_partition_obj.partition = individual
            fitness = self.individual_partition_obj.return_fitness()
            tuple = (fitness, list(individual))
            self.sorted_scored_population.append(tuple)
        
        self.sorted_scored_population.sort(reverse = True)
        
        return self.sorted_scored_population

class GeneticAlgorithm(Population):
    """
    A class that implements the methods of a genetic algorithm 
    
    Attributes
    ----------
    population_obj : Population object
        inherited from the Population class
    generation_number : int
        the current generation the algorithm is on
    mutation_rate : float
        the rate of mutation for each child, with
        a default value of 0.01 (1%)
    current_generation: 
        a deep copy of the sorted_scored_population attribute from population_obj,
        this is a list in the form [(score1, population1), (score2, population2), ...]
    next generation:
        the next generation of individuals as determined by the algorithm, 
        this is a list in the form [(score1, population1), (score2, population2), ...]
    number_of_partitions: int
        inherited from the Population class
    
    Methods
    -------
    mutate(individual_partition)
        a method to mutate children based on a specified mutation rate
    children(parent1, parent2)
        produce two children (new partitions) by performing random
        crossover and mutation on the parents (original partitions)
    run_tournament(scored_population)
        select two parents from the population using Tournament Selection
    generate_next_generation()
    """
    
    def __init__(self, population_obj, generation_number, mutation_rate = 0.01):
        """
        Parameters
        ----------
        population_obj : Population object
            inherited from the Population class
        generation_number : int
            the current generation the algorithm is on
        mutation_rate : float
            the rate of mutation for each child, with
            a default value of 0.01 (1%)
        current_generation: 
            a deep copy of the sorted_scored_population attribute from population_obj,
            this is a list in the form [(score1, population1), (score2, population2), ...]
        next generation:
            the next generation of individuals as determined by the algorithm, 
            this is a list in the form [(score1, population1), (score2, population2), ...]
        number_of_partitions: int
            inherited from the Population class
        """
        self.population_obj = population_obj
        self.generation_number = generation_number
        self.mutation_rate = mutation_rate
        self.current_generation = [(population[0],population[1][:]) for population in population_obj.sorted_scored_population]
        self.next_generation = None
        self.number_of_partitions = population_obj.number_of_partitions
    
    def mutate(self, individual_partition):
        """
        A method to mutate children based on a specified mutation rate
        
        Source: https://en.wikipedia.org/wiki/Mutation_(genetic_algorithm)
        
        Parameters
        ----------
        individual_partition : list
            a list in the form ["A", "A", "B", "D", "A", "C", "B", "C", ...]
        """        
        
        # the list of possible letters based on the value of self.number_of_partitions 
        # this will usually be ["A","B","C","D"]
        letter_list = [chr(i + 65) for i in range(0, self.number_of_partitions)]
        
        # the mutated partition
        new_partition = []
        
        # for each letter in your ["A", "A", "B", "D", "A", "C", "B", "C", ...]:
        for letter in individual_partition: 
            
            # generate a random number between 0 and 1 
            # (rolling the dice to see if we are a winner)
            check_mutate = random.random() 
            
            # if we win our "dice roll", then mutate:
            if check_mutate < self.mutation_rate:
                # subtract the letter from letter_list
                # for example, if letter = "A" and 
                # letter_list = ["A","B","C","D"], then
                # intersected_list = ["B","C","D"]
                intersected_list = [element for element in letter_list if element != letter]
                
                # mutated letter is a random selection from
                # intersected_list:
                new_letter = random.choice(intersected_list)
                
                # append this new_letter to new_partition
                new_partition.append(new_letter)
            
            # if we do not win our dice roll, do not
            # mutate, just append the original letter
            # onto new_partition
            else:
                new_partition.append(letter)
        
        # return the mutated partition
        return new_partition
    
    def children(self, parent1, parent2):
        """
        A method to produce two children (new partitions) by performing random
        crossover and mutation on the parents (original partitions).
        
        Note: this function does not select the parents, it only performs the
        crossover/mutation steps once the parents have been selected
        
        Source (mutation): https://en.wikipedia.org/wiki/Mutation_(genetic_algorithm)
        Source (crossover): https://en.wikipedia.org/wiki/Crossover_(genetic_algorithm)
        
        Parameters
        ----------
        parent1 : list
            a list in the form ["A", "A", "B", "D", "A", "C", "B", "C", ...]
        parent2 : list
            a list in the form ["A", "A", "B", "D", "A", "C", "B", "C", ...]
        """    
        
        # the length of the parent lists
        genome_length = len(parent1)
        
        # determine a random cutpoint 
        cutpoint = random.randint(1, genome_length - 1)
        
        # slice both parents at the cutpoint:
        parent1_slice1 = parent1[:cutpoint] 
        parent1_slice2 = parent1[cutpoint:] 
        
        parent2_slice1 = parent2[:cutpoint] 
        parent2_slice2 = parent2[cutpoint:] 
        
        # create the children by combining the slices (crossover)
        child1 = parent1_slice1 + parent2_slice2
        child2 = parent2_slice1 + parent1_slice2
        
        # mutate:
        mutated_child1 = self.mutate(child1)
        mutated_child2 = self.mutate(child2)
        
        # return the children as a tuple:
        return mutated_child1, mutated_child2

    def run_tournament(self, scored_population):
        """
        A method to select two parents from the population. This algorithm
        uses Tournament Selection, though there may be performance gains 
        from trying other selection methods or modifying the size of the 
        tournament. 
        
        Source (selection): https://en.wikipedia.org/wiki/Genetic_algorithm#Selection
        Source (tournament selection): https://en.wikipedia.org/wiki/Tournament_selection
        
        Parameters
        ----------
        scored_population : list
            a list of individuals in the form [partition1, partition2, partition3,...], 
            where the list is sorted in descending fitness order 
            (that is, fitness(partitionX) > fitness(partitionY) for X < Y)

        """         
        scored_population_length = len(scored_population)

        # select three individuals at random from the population
        tournament_member1 = random.randint(0,scored_population_length - 1)
        tournament_member2 = random.randint(0,scored_population_length - 1)
        tournament_member3 = random.randint(0,scored_population_length - 1)
            
        # we want our parents to have the largest weighted_fitness_score possible
        #
        # since the individuals are sorted by descending fitness scores, 
        # the winner of the tournament will be the individual at the smallest index:
        parent1_index = min(tournament_member1, tournament_member2, tournament_member3)
        # we have selected our first parent:
        parent1 = list(scored_population[parent1_index])
        
        # repeat for parent2:    
        tournament_member1 = random.randint(0,scored_population_length - 1)
        tournament_member2 = random.randint(0,scored_population_length - 1)
        tournament_member3 = random.randint(0,scored_population_length - 1)
            
        parent2_index = min(tournament_member1, tournament_member2, tournament_member3)
        parent2 = list(scored_population[parent2_index])
        
        # return the parents as a tuple:
        return parent1, parent2
           
    def generate_next_generation(self):
        """
        The main method of the GeneticAlgorithm class: use self.current_generation
        to generate self.next_generation
        
        Source: https://en.wikipedia.org/wiki/Genetic_algorithm
        
        Parameters
        ----------
        None
        """ 
        # the next_generation should be the same length as the current_generation
        next_generation_length = len(self.current_generation)
        
        # Use elitist selection for 20% of self.next_generation
        # Source: https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#e._Elitism_Selection
        elites_length = 2*next_generation_length//10
        
        # Introduce completely new individuals for 10% of self.next_generation
        new_blood_length = next_generation_length//10
        
        # Use crossover for the remaining 70% of self_next_generation
        # Source: https://en.wikipedia.org/wiki/Crossover_(genetic_algorithm)
        children_length = next_generation_length - elites_length - new_blood_length
        
        # A container for the list of individuals that will be added to self.next_generation
        # This initial list starts out unscored: [partition1, partition2, partition3,...]
        next_generation_individuals = []
        
        # A list of elites (the fittest 20% of the self.current_generation)
        # This list is in the form [partition1, partition2, partition3,...]
        elites = [item[1] for item in self.current_generation[0:elites_length]]
        
        # Add these to the next_generation_individuals
        next_generation_individuals.extend(elites)
        
        # Generate the "new blood" (the 10% completely random individuals)
        # Note: these individuals are currently unscored
        for i in range(new_blood_length):
            ith_partition = self.population_obj.generate_individual()
            next_generation_individuals.append(ith_partition)

        # A list of all individuals from self.current_generation, 
        # these are the potential parents for self.next_generation
        # Note: this list is in the form [partition1, partition2, partition3,...]
        ordered_individuals = [element[1][:] for element in self.current_generation]

        # For the remaining 70% of individuals in self.next_generation, 
        # do the following:
        # 1) Select two parents using tournament selection
        # 2) Generate two children using crossover & mutation
        for i in range(children_length//2):
            
            parent1, parent2 = self.run_tournament(ordered_individuals)
            
            child1, child2 = self.children(parent1, parent2)
            
            next_generation_individuals.extend([child1, child2])
            
            # We are generating children in pairs, if we accidentally
            # add one child too many to self.next_generation, take off 
            # the extra child 
            if len(next_generation_individuals) > next_generation_length: 
                next_generation_individuals = next_generation_individuals[0:-1]
        
        # next_generation_individuals has not yet been scored, so we
        # use the Population class to assess the fitness of the next_generation:
        self.population_obj.population = next_generation_individuals
        self.population_obj.sorted_scored_population = []
        scored_next_generation = self.population_obj.population_fitness()
        
        # after scoring, assign this to self.next_generation
        # self.next_generation is in the form [(score1, partition1), (score2, partition2), ...]
        self.next_generation = scored_next_generation
        
        return self.population_obj.sorted_scored_population

def run_loop(path, number_of_partitions, pop_size, rate_of_mutation, max_gen, max_time):
    """
    Repeat the Genetic Algorithm based on a specified number of generations (or time limit)
                
    Parameters
    ----------
    path : str
        the location of the input.csv
    number_of_partitions: int
        the number of partitions to group students into
        2 for an A/B partition
        4 for an A/B/C/D partition
        Note: Other values are not implemented
    pop_size: int
        the size of the population in the genetic algorithm
    rate_of_mutation: float
        the mutation rate in the genetic algorithm
    max_gen: int
        the maximum number of generations to run the algorithm
    max_time: int
        the maximum number of minutes to run the algorithm
    """     
    # if you open a .csv report in Microsoft Excel and leave it open,
    # this program will throw a PermissionError when it tries to write
    # the new .csv report
    #
    # this warning is to remind you to close these .csv files before this
    # happens
    #
    warnings.warn("To avoid permission errors, close any output files you may have left open from previous runs.")
    
    # initializer the timer to 0
    timer_total = 0
    
    # start the timer
    start_timer = time.perf_counter()
    
    generation_number = 1
    
    # instantiate the Schedule object
    load_schedule = Schedule(number_of_partitions)
    
    # load school data into the Schedule object
    load_schedule.students_from_csv(path)
    
    # instantiate the IndividualPartition object
    first_partition = IndividualPartition(load_schedule)
    
    # instatiate the Population object
    population = Population(first_partition, pop_size)
    
    # populate with random individuals for the first generation
    population.populate()
    
    # score this initial population
    population.population_fitness()
    
    # instantiate the GeneticAlgorithm object
    first_generation = GeneticAlgorithm(population, generation_number, rate_of_mutation)
    
    # generate Generation #2
    first_generation.generate_next_generation()
    previous_population = first_generation.next_generation
    
    # track the time this process took:
    end_timer = time.perf_counter()
    timer_total += end_timer - start_timer

    # Uncomment below to track how long this took:
    #print("Benchmark result = " + str(end - start))

    # Concatenate a string to report progress:
    progress_string = "Generation = "
    progress_string += str(generation_number)
    progress_string += ", Fitness = "
    progress_string += str(previous_population[0][0][0])
    progress_string += ", In Compliance = "
    progress_string += str(previous_population[0][0][2])
    progress_string += " out of "
    progress_string += str(previous_population[0][0][-1])   
    
    # Print progress & write to the progress log:
    print(progress_string)

    progress_file = IO_DIRECTORY + 'progress_log.txt'    
    with open(progress_file, 'w') as file:
        file.write(progress_string)
        file.write("\n")   

    # keep repeating this process until the maximum number
    # of generations or the time limit has been reached
    while generation_number < max_gen and timer_total < 60*max_time:
        
        # same process as above
        start_timer = time.perf_counter()
        
        generation_number += 1
        
        population.sorted_scored_population = previous_population
        current_generation = GeneticAlgorithm(population, generation_number, rate_of_mutation)
        current_generation.generate_next_generation()
        previous_population = current_generation.next_generation
        
        end_timer = time.perf_counter()
        timer_total += end_timer - start_timer
        
        progress_string = "Generation = "
        progress_string += str(generation_number)
        progress_string += ", Fitness = "
        progress_string += str(previous_population[0][0][0])
        progress_string += ", In Compliance = "
        progress_string += str(previous_population[0][0][2])
        progress_string += " out of "
        progress_string += str(previous_population[0][0][-1])
        
        print(progress_string)

        with open(progress_file, 'a') as file:
            file.write(progress_string)
            file.write("\n") 
        
        # every 100 generations, write reports on student assignments
        # and a course-by-course analysis:
        if generation_number % 100 == 0:
            intermediate_partition = previous_population[0][1]
    
            load_schedule.load_partition(intermediate_partition)
            
            load_schedule.write_student_assignments()
    
            load_schedule.write_course_analysis()
        
        if timer_total >= 60 * max_time:
            print("Time limit reached: Ended after generation #" + str(generation_number))
        elif generation_number >= max_gen:
            print("Generation limit reached: Ended after generation #" + str(generation_number))
    
    # at the end of the algorithm, write a student assignment report
    # and a course-by-course analysis report
    final_partition = previous_population[0][1]
    
    load_schedule.load_partition(final_partition)
    
    load_schedule.write_student_assignments()
    
    load_schedule.write_course_analysis()

# a possible target for using the multiprocessing module:     
def main():
    run_loop(IO_DIRECTORY + INPUT_CSV_FILENAME, NUMBER_OF_PARTITIONS, POPULATION_SIZE, MUTATION_RATE, NUMBER_OF_GENERATIONS, TIME_LIMIT)

if __name__ == "__main__":
    main()


