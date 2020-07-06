"""
Name: Student Partition Optimization Tool for Schools (SPOTS)

Version: 1.0.0a4

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
import multiprocessing # run the genetic algorithm in parallel on multiple cores
import os   # used for getting the process ID via os.getpid()
from pathlib import Path 

# SCHOOL-SPECIFIC SETTINGS:

# number of groups to partition students into (only 2 and 4 are implemented)
NUMBER_OF_PARTITIONS = 4

# time measured in minutes (default = 480 min or 8 hr)
TIME_LIMIT = 60*8 

# max size of a partition when dividing students into two cohorts (default = 15) 
HALF_CLASS_MAXIMUM = 15 

# max size of a partition when dividing students into four cohorts (default = 9)
QUARTER_CLASS_MAXIMUM = 9

# filename of .csv file with student schedule data (default = "example_student_data.csv) 
INPUT_CSV_FILENAME = "example_student_data.csv" 

# filename of .csv file with required student subgrouping data (default = "example_subgroups.csv") 
REQUIRED_SUBGROUP_CSV_FILENAME = "example_subgroups.csv" 
# if no required subgroups are needed, set the above value to None

# filename of .csv file with preferred student subgrouping data (default = None) 
PREFERRED_SUBGROUP_CSV_FILENAME = None
# if no preferred subgroups are needed, set the above value to None

# GENETIC ALGORITHM SETTINGS
# 
# If you experiment with the following settings, you may happen upon a 
# combination of values that optimizes more efficiently than the default 
# settings in this program. If so, please share these values with me at 
# studentpartitionoptimizer@gmail.com so I can verify and make these the 
# new defaults. 

# number of processes to launch
NUMBER_OF_PROCESSES = multiprocessing.cpu_count()

# for the tournament selection when crossbreeding across islands,
# the number of representatives to use. the below seems to work
# well in practice.
NUMBER_OF_TOURNAMENT_REPS_PER_ISLAND = NUMBER_OF_PROCESSES//4

# recommended range: between 0.01 and 0.05, (default = 0.01)
MUTATION_RATE = 0.01

# on my 16-core machine, this seems to work best
# (for each core/island, during the end-of-era crossbreeding stage:
# 25% elites = top 15, then the remaining 45 is made up of
# [15 neighboring islands to cross with] * [3 partitions per island]
# the "right" value here is going to depend a lot on number of cores,
# so you can play around with this to see what seems to work best
# recommended range, at least according to my experimentation: 20 - 80
POPULATION_SIZE = 60

# recommended range: run it for as long as you have time, or until the
# [number of compliant sections] metric seems to plateau out.
NUMBER_OF_ERAS = 5000

# in my experience while testing with 16 cores, a small number here made sense
# (with more frequent crossbreeding between islands). i believe this is because
# there are a lot of islands to cross with, and with 15 neighboring islands chances are
# good that one of your neighbors has found some opimization feature that you haven't yet
# if you have fewer cores, then i think this number should probably increase a bit
# recommended range, at least according to my experimentation: 10 - 50
NUMBER_OF_GENERATIONS_PER_ERA = 20

# I/O DIRECTORY

# gets the location of the .py file (also where input .csv files should be)
IO_DIRECTORY = Path(os.path.dirname(__file__))

# use pathlib Path object to convert slashes for
# the current operating system
INPUT_CSV_FILENAME = IO_DIRECTORY / INPUT_CSV_FILENAME

if REQUIRED_SUBGROUP_CSV_FILENAME is not None:
    REQUIRED_SUBGROUP_CSV_FILENAME = IO_DIRECTORY / REQUIRED_SUBGROUP_CSV_FILENAME

if PREFERRED_SUBGROUP_CSV_FILENAME is not None:
    PREFERRED_SUBGROUP_CSV_FILENAME = IO_DIRECTORY / PREFERRED_SUBGROUP_CSV_FILENAME

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
    half_class_maximum : int
        the target maximum size of a partition when dividing students 
        into two cohorts of roughtly equal size
        (default value is 15)
    quarter_class_maximum : int
        the target maximum size of a partition when dividing students
        into four cohorts of roughly equal size
        (default value is 9)
    student_list : list
        an ordered list of student objects, where each student object
        represents a single student at the school
    student_dict : dict
        key: a student ID number (a unique identifier for a student)
        value: the associated student object
    course_dict : dict
        key: a course object
        value: a course roster (a list of student objects enrolled 
        in the course)
    required_subgroups_list : list
        a list of tuples, where each tuple is a subgroup of students
        that must be assigned to the same letter group
        
        example: here is a list where students 1/2/3 must be assigned 
        to the same letter, students 3/4 must be assigned to the same 
        letter, and student6 is in a subgroup by him/herself:
        
        [(student1, student2, student3), (student4, student5), (student6)]
        
    preferred_subgroups_list : list
        a list in the same form as required_subgroups_list, but subgroups
        are not required by the algorithm 
        (instead, this will be encouraged by the fitness function)
            
    Methods
    -------
    students_from_csv(file_location)
        populates student_list and course_dict from a .csv file
    subgroups_from_csv(file_location, required_or_preferred)
        populates required_subgroups_list and/or preferred_subgroups from
        a .csv file        
    load_partition(letter_list)
        load a list of letter assignments into the letter attribute
        for each cohort of student objects in Schedule.required_subgroups_list
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
    
    def __init__(self, number_of_partitions = 4, half_class_maximum = 15, quarter_class_maximum = 9):
        """
        The constructor for the Schedule class
        
        Parameters
        ----------
        number_of_partitions : int
            the number of partitions students are to be separated into 
            (default value is 4)
        half_class_maximum : int
            the target maximum size of a partition when dividing students 
            into two cohorts of roughtly equal size
            (default value is 15)
        quarter_class_maximum : int
            the target maximum size of a partition when dividing students
            into four cohorts of roughly equal size
            (default value is 9)
        """
        self.number_of_partitions = number_of_partitions
        self.half_class_maximum = half_class_maximum
        self.quarter_class_maximum = quarter_class_maximum
        
        # changed student_list to a list so users using old versions of Python (< 3.7) 
        # do not run into issues with iterating over a dictionary in a deterministic order
        # 
        # Python 3.7: dictionary order guaranteed to be in insertion order:
        # https://docs.python.org/3/library/stdtypes.html#dict, dictionary order 
        #
        # before Python 3.7, dictionary order was not guaranteed
        #
        self.student_list = []
        self.student_dict = None
        self.course_dict = {}
        
        self.required_subgroups_list = None
        self.preferred_subgroups_list = None        

    def subgroups_from_csv(self, file_location, required_or_preferred):
        """
        A method to populate required_subgroups_list and preferred_subgroups_list
        from a .csv file
        
        The .csv file should have two columns, each representing a pairing:

        ID Num 1, ID Num 2
        09281381, 20383882
        42074738, 87172918
        09281381, 63471199
        87172918, 42074738
        87172918, 59283715
        
        Suppose most ID numbers correspond to a Student object:
        
        student1.id = '09281381'
        student2.id = '20383882'
        student3.id = '42074738'
        student4.id = '87172918'
        student5.id = '63471199'
        
        For this example, suppose that '59283715' is an invalid ID number, and has
        no student associated to it. 
        
        Here is how this method will parse this list of pairings: 
        
        Look at the first row "09281381, 20383882". This row indicates that 
        student1 and student2 are part of a subgroup. Append these:
        
        temp_subgroups_list = [[student1, student2]]
        
        The second row indicates that student3 and student 4 are in a 
        subgroup, so update the list as follows:
        
        temp_subgroups_list = [[student1, student2], [student3, student4]]
        
        The third row indicates that student5 should be added to the subgroup
        containing student1: 
        
        temp_subgroups_list = [[student1, student2, student5], [student3, student4]]

        The fourth row is superfluous since student3 and student4 are already in
        a subgroup, so no action is taken.
        
        The fifth row pairs student4 with a non-existent student, so no action
        is taken. 
        
        Next, convert our nested list into a list of tuples:
        
        temp_subgroups_list = [(student1, student2, student5), (student3, student4)]
   
        Finally, we check student_list against temp_subgroups_list. Each student
        in student_list that is not in temp_subgroups_list represents a subgroup
        of size 1. We append these to temp_subgroups_list. For example, suppose 
        we have the following: 
        
        student_list = [student1, student2, student3, student4, student5, student6]
        
        Then we write the following: 
        
        temp_subgroups_list = [(student1, student2, student5), (student3, student4), (student5), (student6)]
        
        If required_or_preferred = "required", we assign self.required_subgroups_list = temp_subgroups_list
        
        If required_or_preferred = "preferred", we assign self.preferred_subgroups_list = temp_subgroups_list
        
        Parameters
        ----------
        csv_file_location : str
            the file path of a .csv file with student pairing data, for 
            example C:\\Users\\jsmith\\student_pairings.csv
        """
        
        # we only want to do something if file_location 
        # is not set to "None":
        
        # if file_location is None and require_or_preferred = "required"
        # then all of our subgroups are of size 1 (each student comprises
        # their own subgroup):
        if file_location is None and required_or_preferred == "required":
            # our required_subgroups_list is a list of tuples each 
            # containing a single Student object, which is represented
            # as a tuple with a trailing comma:
            self.required_subgroups_list = [(student,) for student in self.student_list] 

        # otherwise, if there is a file to read:
        elif file_location is not None:
            # import the .csv:
            with open(file_location, mode='r') as infile:
                
                # a place to store subgroups
                temp_subgroups_list = []
                
                # read the .csv file            
                reader = csv.reader(infile)
                
                # skip the first row since the first row contains headers
                next(reader) 
                
                # description of the columns in the .csv file:
                for row in reader:
                    # row[0] : First student ID number
                    first_id = row[0]
                    
                    # row[1] : Second student ID number
                    second_id = row[1]
                    
                    # check if both student ID numbers are valid by checking
                    # if the ID numbers are keys in self.student_dict:
                    if first_id in self.student_dict and second_id in self.student_dict:
                        # if they are, then store the Student objects:
                        student_obj1 = self.student_dict[first_id]
                        student_obj2 = self.student_dict[second_id]
                        
                        # if temp_subgroups_list is empty, then we have our first subgroup,
                        # which we store as [[student_obj1, student_obj2]]
                        if len(temp_subgroups_list) == 0:
                            temp_subgroups_list.append([student_obj1, student_obj2])
                        # otherwise, we need to check whether we have to append to 
                        # an existing subgroup or create a new one:
                        else: 
                            
                            # use found_flag to track if we have found a subgroup 
                            # containing student_obj1 or student_obj2:
                            found_flag = False
                            
                            # for each existing subgroup
                            for subgroup in temp_subgroups_list:
                                # if both student objects are in the subgroup, then we 
                                # are done with these two student objects 
                                if student_obj1 in subgroup and student_obj2 in subgroup:
                                    # set found_flag to True to indicate that we have managed
                                    # to verify that our students are already in a subgroup
                                    found_flag = True
                                    
                                    # at this point, there is no reason to continue with the current
                                    # loop so we break:
                                    break                                    
                                    
                                # if student_obj1 is in the subgroup, but student_obj2 is not, 
                                # then add student_obj2 to the subgroup:                                    
                                elif student_obj1 in subgroup and student_obj2 not in subgroup:
                                    subgroup.append(student_obj2)
                                    
                                    # set found_flag to True to indicate that we have managed
                                    # to fit our students into a subgroup
                                    found_flag = True
                                    
                                    # at this point, there is no reason to continue with the current
                                    # loop so we break:
                                    break
                                    
                                # similarly, if student_obj1 is NOT in the subgroup but 
                                # student_obj2 is, then add student_obj1 to the subgroup:                            
                                elif student_obj1 not in subgroup and student_obj2 in subgroup:
                                    subgroup.append(student_obj1)
                                    
                                    # set found_flag to True to indicate that we have managed
                                    # to fit our students into a subgroup
                                    found_flag = True
                                    
                                    # at this point, there is no reason to continue with the current
                                    # loop so we break:
                                    break                                
                            
                            # if the above for loop completes without finding a subgroup, then
                            # found_flag will remain False and we also know the following: 
                            #
                            # 1. student_obj1 and student_obj2 are valid students
                            # 2. these students are not a part of any existing subgroup
                            #
                            # in this case we create a new subgroup with the student objects
                            if found_flag is not True:
                                temp_subgroups_list.append([student_obj1, student_obj2])
                
                # once we have completed this for every row of the .csv, we have successfully
                # populated temp_subgroups_list with every student subgroup of size > 1
                
                # since we are done appending to subgroups, convert to a list of tuples:            
                temp_subgroups_list = [tuple(subgroup) for subgroup in temp_subgroups_list]
               
                # finally, each Student object that is in student_list but does not 
                # currently appear in a subgroup is actually a subgroup of length 1
                #
                # we need to add these to temp_subgroups_list:
                
                # for each Student_object in self.student_list
                for student_obj in self.student_list:
                    
                    # a flag to indicate that we have not found 
                    # the student in a subgroup yet
                    found_flag = False                   
                    
                    # for each existing subgroup:
                    for subgroup in temp_subgroups_list:                       
                        
                        # if the student object is found in the subgroup
                        if student_obj in subgroup:
                            
                            # then the student has been found
                            found_flag = True
                            
                            # and we can break out of the loop
                            break
                        # if we reach subgroups of length 1
                        elif len(subgroup) == 1:
                            # then we can stop our search because we 
                            # know that student_obj needs to be added
                            # to temp_subgroups_list as a subgroup of 
                            # length 1
                            break
                            
                    # if we have not found the flag ("not found_flag" evaluates to True)
                    if found_flag is not True:
                        # then append the student to temp_subgroups_list as a subgroup
                        # of length 1:
                        temp_subgroups_list.append((student_obj,)) # singleton tuple needs a trailing comma
                
                # now temp_subbroups_list is fully populated, 
                # so we assign it to the appropriate attribute:
                if required_or_preferred == "required":
                    self.required_subgroups_list = temp_subgroups_list
                elif required_or_preferred == "preferred":
                    self.preferred_subgroups_list = temp_subgroups_list
                else: 
                    raise NameError('Subgroups must either be "required" or "preferred"')
                
                    
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
            # self.student_dict is a dictionary with the following:
            # key: ID number
            # value: associated Student object
            self.student_dict = {}
            
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
                
                # check if student_id is NOT in our self.student_dict
                if student_id not in self.student_dict:
                    # if the student is not in self.student_dict,
                    # then instantiate a Student object and assign 
                    # it to current_student:
                    current_student = Student(student_id)
                    current_student.last_name = last_name
                    current_student.middle_name = middle_name
                    current_student.first_name = first_name

                    # next, add to self.student_dict using:
                    # key: student_id 
                    # value: Student object
                    self.student_dict[student_id] = current_student                    
                    
                # otherwise, student_id **is** in our self.student_dict:
                else:
                    # access this Student object and assign it to current_student:
                    current_student = self.student_dict[student_id]

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

            # now that self.student_dict has a unique key for each 
            # student, we can iterate over the dictionary to populate
            # our student_list with tuples in the form (student, schedule):
            # student: a Student object 
            #       (a student at the school)
            # schedule: a list of Course objects the student is taking 
            #       (aka: a course schedule)    
            
            for key in self.student_dict:
                student_obj = self.student_dict[key]
                schedule = student_obj.schedule
                self.student_list.append(student_obj)

    def load_partition(self, letter_list):
        """
        A method to load a list of letters into the letter attribute for 
        each student object in Schedule.student_list
        
        For example, suppose letter_list = ["A", "B", "D"]. Also suppose that 
        required_subgroups_list = [(student_obj1, student_obj2), (student_obj3,), (student_obj4,)].
        Then Schedule.load_partition(letter_list) would lead to the following result:
        
        student_obj1.letter = "A"
        student_obj2.letter = "A"
        student_obj3.letter = "B"
        student_obj4.letter = "D"
        
        This method is used when we need to evaluate the fitness of a newly-generated partition.
        
        Parameters
        ----------
        letter_list : list
            a list of letter assignments for each subgroup at the school, for example a school with
            four subgroups could have ["A", "B", "A", "D"]
        """

        number_of_partitions = self.number_of_partitions
        
        for i in range(len(letter_list)):
            letter = letter_list[i]
            
            # get the subgroup from the list
            student_subgroup = self.required_subgroups_list[i]
            
            # assign the same letter to every student in the subgroup
            for student in student_subgroup:
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
        output_file = IO_DIRECTORY / 'student_assignments.csv' 
        
        with open(output_file, 'w') as file:
            # write the headers of the .csv
            headers = "id,last name,first name,middle name,letter"
            file.write(headers)
            file.write("\n")   
            
            # write a line in the .csv for each student in student_list:
            for student_obj in self.student_list:
                current_id = student_obj.id
                current_last = student_obj.last_name
                current_first = student_obj.first_name
                current_middle = student_obj.middle_name
                current_letter = student_obj.letter
                
                line = current_id + "," + current_last + "," + current_first + "," + current_middle + "," + current_letter
                
                file.write(line)
                
                file.write("\n")

    # TO DO: UPDATE THIS ANALYSIS TO AGREE WITH THE FITNESS FUNCTION
    # THE NEW FITNESS FUNCTION COUNTS MORE SECTIONS AS "IN COMPLIANCE",
    # WHICH EITHER NEEDS TO BE CHANGED BACK OR INCORPORATED INTO THIS
    # ANALYSIS SO THAT THE RESULTS ARE CONSISTENT
    
    # TO DO: UPDATE CODE BELOW TO EMULATE @jmoon81's CHANGES TO THE 
    # FITNESS FUNCTION. FOR EXAMPLE, DO NOT USE THE FOLLOWING: 
    # possible_letter_list = [chr(i + 65) for i in range(0, self.number_of_partitions)]
    # THIS IS BECAUSE HE ALREADY HARD CODED THE FOLLOWING: 
    # if NUMBER_OF_PARTITIONS == 2:
    #   STUDENT_LETTER_LIST = ["A", "B"]
    # elif NUMBER_OF_PARTITIONS == 4:
    #   STUDENT_LETTER_LIST = ["A", "B", "C", "D"]
    
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
        requirements since each A/B/C/D cohort is self.quarter_class_maximum (9)
        or fewer students.
        
        Example data #2:
        201,6,[E10101], 32, 10, 6, 8, 8, 0.3125, 0.1875, 0.25, 0.25, 0.0625, No
        
        This example says that the class in Rm 201 during 6th hour has
        32 students, with 10 A's, 6 B's, 6 C's, 6 D's. The A's comprise
        31.25% of the class, the B's are 18.75% of the class, and the 
        C's/D's are each 25% of the class. The max deviation is 0.0625, 
        which is found by 0.3125 - 0.25 = 0.0625. This course is NOT in 
        compliance with physical distancing requirements since the A-group
        exceeds self.quarter_class_maximum (9) students. 
                
        Parameters
        ----------
        None
        """
        # the file name and location for the course analysis report:
        output_file = IO_DIRECTORY / 'course_analysis.csv' 
        
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
                        if counts[0] <= self.half_class_maximum and counts[1] <= self.half_class_maximum:
                            line += "Yes" 
                        else:
                            line += "No"
                        
                    elif self.number_of_partitions == 4:
                        a_count = counts[0]
                        b_count = counts[1]
                        c_count = counts[2]
                        d_count = counts[3]
                        
                        # for an A/B/C/D partition, we say that a course is
                        # "In Compliance" if there are no more than 
                        # self.quarter_class_maximum (9) students in any
                        # of the four groups:
                        
                        qcm = self.quarter_class_maximum 
                        check_individually = (a_count <= qcm 
                                            and b_count <= qcm 
                                            and c_count <= qcm 
                                            and d_count <= qcm)
                        
                        # we also require that the (A+B) and (C+D) combined 
                        # groups are no more than self.half_class_maximum students
                        # (default value 15):                        
                        check_pairs = (a_count + b_count <= self.half_class_maximum 
                                    and c_count + d_count <= self.half_class_maximum)
                        
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
                # if it has no more than self.half_class_maximum
                # A's and self.half_class_maximum B's (default 
                # value is 15):
                hcm = self.half_class_maximum
                
                # our tolerance for applying a penalty based on the 
                # the ratio of A to B groups (usually set to 55%) 
                # 
                # for a small class, 55% might not be feasible, so we set
                # it to (total/2 + 1)/total instead
                #                
                pairwise_tolerance = max([0.55, (total/2+1)/total])
                
                if a_count <= hcm and b_count <= hcm:
                    # increment the raw "In Compliance" score:
                    good_score += 1 
                    # increment the weighted_fitness_score
                    # note that if all classes were "good" then 
                    # the fitness score would equal 100 since
                    # number_of_courses*(100/number_of_courses) = 100
                    weighted_fitness_score += 100/number_of_courses 
                # otherwise, apply a penalty based on how far the course
                # deviates from a 50/50 split betwen A's and B':
                elif a_count <= hcm and b_count > hcm:
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                elif a_count > hcm and b_count <= hcm:
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                # If we make it here, a_count and b_count are 
                # both above self.half_class_maximum (15), so 
                # no partition can ever get both
                # a_count <= self.half_class_maximum
                #   and 
                # b_count <= self.half_class_maximum 
                # at the same time. 
                # Instead we try to make sure that the relative
                # ratio between A's and B's is better than a 
                # pairwise_tolerance split:
                elif a_percent > pairwise_tolerance:
                    # penalize if the section deviates from a 
                    # pairwise_tolerance split between A/B
                    weighted_fitness_score -= percent_difference
                    penalty_count += 1
                elif b_percent > pairwise_tolerance: 
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
                                
                # check if there are no more than self.quarter_class_maximum
                # (9) students of any letter:
                qcm = self.quarter_class_maximum
                check_individually = (a_count <= qcm 
                                    and b_count <= qcm 
                                    and c_count <= qcm 
                                    and d_count <= qcm)
                
                # check if the (A+B) count and (C+D) count are each less
                # than self.half_class_maximum students (default value is 15):
                hcm = self.half_class_maximum
                check_pairs = (a_count + b_count <= hcm and c_count + d_count <= hcm)
                
                # we classify a course as "In Compliance" if there
                # are no more than self.quarter_class_maximum (9) 
                # students of any letter, and if the (A+B) count 
                # and the (C+D) are each less than or equal to 
                # self.half_class_maximum (15)
                if check_individually and check_pairs:
                    # increment the raw "In Compliance" score:
                    good_score += 1
                    # increment the weighted_fitness_score:
                    weighted_fitness_score += 100/number_of_courses

                # otherwise, start subtracting from the weighted_fitness_score, 
                # where penalties are applied based on how far the course deviates
                # from an even distribution of A/B/C/D:
                else: 
                    # pairwise_multiplier: 
                    #
                    # change this depending on what you want to emphasize in the search:
                    #
                    # increase to emphasize an even distribution between the (A+B) and
                    # (C+D) groups (work towards a 50/50 split between these groups)
                    # 
                    # decrease to emphasize "In Compliance" courses
                    #
                    # default value of pairwise_multiplier = 0.3
                    #
                    pairwise_multiplier = 0.3
                    
                    # individual_multiplier
                    #
                    # change this depending on what you want to emphasize in the search:
                    #
                    # increase to emphasize an even distribution between the A/B/C/D groups
                    #
                    # decrease to emphasize "In Compliance" courses                    
                    # 
                    # default of individual_multiplier = 0.25
                    #
                    individual_multiplier = 0.25


                    # relative percentage of A's/B's/C's/D's:
                    a_percent = a_count/total
                    b_percent = b_count/total
                    c_percent = c_count/total
                    d_percent = d_count/total

                    # our tolerance for applying a penalty based on the 
                    # relative size of the (A + B) or (C + D) groups, 
                    # which is usually going to be set to 55%
                    # 
                    # for a small class, 55% might not be feasible, so we set
                    # it to (total/2 + 1)/total instead
                    #
                    pairwise_tolerance = max([0.55, (total/2+1)/total])

                    if a_percent + b_percent > pairwise_tolerance:
                        # see note above about pairwise_multiplier
                        weighted_fitness_score -= pairwise_multiplier*(a_percent + b_percent - 0.5)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if c_percent + d_percent
                    # exceeds the value of pairwise_tolerance:
                    elif c_percent + d_percent > pairwise_tolerance:
                        # see note above about pairwise_multiplier
                        weighted_fitness_score -= pairwise_multiplier*(c_percent + d_percent - 0.5)
                        penalty_count += 1

                    # our tolerance for applying a penalty based on the 
                    # relative size of any individual A/B/C/D group
                    # which is usually going to be set to 30%
                    # 
                    # for a small class, 30% might not be feasible, so we set
                    # it to (total/4 + 1)/total instead
                    #
                    individual_tolerance = max([0.3, (total/4+1)/total])

                    # subtract from weighted_fitness_score if a_percent exceeds the value of individual_tolerance:
                    if a_percent > individual_tolerance:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(a_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if b_percent exceeds 30% of the roster:
                    if b_percent > individual_tolerance:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(b_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if c_percent exceeds 30% of the roster:
                    if c_percent > individual_tolerance:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(c_percent - 0.25)
                        penalty_count += 1
                    # subtract from weighted_fitness_score if d_percent exceeds 30% of the roster:
                    if d_percent > individual_tolerance:
                        # see note above about individual_multiplier
                        weighted_fitness_score -= individual_multiplier*(d_percent - 0.25)
                        penalty_count += 1
                   
                    # an "Out of Compliance" section for which no penalty was applied:                    
                    
                    all_individually = (a_percent <= individual_tolerance
                                        and b_percent <= individual_tolerance 
                                        and c_percent <= individual_tolerance 
                                        and d_percent <= individual_tolerance)
                   
                    all_pairwise = (a_percent + b_percent <= pairwise_tolerance
                              and (c_percent + d_percent) <= pairwise_tolerance)
                    
                    if all_individually and all_pairwise:
                        if total > 2*hcm:
                            # this is a course that is too big to ever be 
                            # "In Compliance" above, but we have at least 
                            # partitioned it evenly, so we count it as good:
                            weighted_fitness_score += 100/number_of_courses
                            
                            # TO DO: DEBATE WHETHER INCREMENTING HERE IS GOOD
                            # PRACTICE. THIS COURSE IS 'AS GOOD AS IT CAN GET'
                            # IN A SENSE BECAUSE IT CAN NEVER SATISFY THE 
                            # REQUIREMENT SET BY self.half_class_maximum
                            good_score += 1
                        else:
                            # this should catch any cases that have been missed above 
                            other_score += 1
                            
        else:
            print("In order to choose something other than an AB or ABCD partition, you must add your own fitness function")    
            raise NotImplementedError
        
        if self.preferred_subgroups_list is not None:
            number_of_subgroups = len(self.preferred_subgroups_list)
            
            for subgroup in self.preferred_subgroups_list:
                subgroup_letter_set = {}
                
                for student in subgroup:
                    subgroup_letter_set.add(student.letter)
                    
                if len(subgroup_letter_set) > 1:
                    # TO DO: DISCUSS THE BEST APPROACH FOR PENALIZING
                    # VIOLATIONS OF PREFERRED_SUBGROUPS AND HOW TO APPLY
                    # THE PENALTY
                    #
                    # SHOULD THE PENALTY BASED ON HOW SEVERE THE VIOLATION IS
                    # OR SIMPLY A RECOGNITION OF THE FACT THAT THE SUBGROUP
                    # IS NOT ASSIGNED TO THE SAME LETTER?
                    #
                    # IF THE SIZE OF THE VIOLATION MATTERS, THEN WE SHOULD USE 
                    # subgroup_letter_list = [] INSTEAD OF SETS
                    # AND subgroup_letter_list.append(student.letter) INSTEAD OF .add
                    weighted_fitness_score -= 100/number_of_subgroups
        
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

        for student in self.student_list:
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
    A class used to store an individual partition of student
    subgroups as an ordered list of letter assignments
    
    Ex: ["A", "A", "C", "B", "D", "A", ...]
    
    Attributes
    ----------
    schedule_obj: Schedule object
        inherited from the schedule class
    
    number_of_partitions: int
        inherited from the schedule class
        
    partition : list
        an individual partition of student subgroups stored as a 
        list of letters, ex: ["A", "A", "C", "B", "D", "A", ...]
        
    fitness: tuple
        a tuple representing the fitness of the partition in the form:
        (weighted_fitness_score, penalty_count, good_score, other_score, number_of_courses)
    
    student_letter_list : list
        either ["A", "B"] or ["A", "B", "C", "D"]    
    
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
        
        if self.number_of_partitions == 2:
            self.student_letter_list = ["A", "B"]
        elif self.number_of_partitions == 4:
            self.student_letter_list = ["A", "B", "C", "D"]
                
        self.partition = None
        self.fitness = None

    def generate_partition(self):
        """
        A method to generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
        
        Parameters
        ----------
        None
        
        """        
        
        student_partition_list = []
    
        # use number_of_subgroups to determine how many letters are needed
        number_of_subgroups = len(self.schedule_obj.required_subgroups_list)

        # populate the list, ex: ["A", "A", "C", "B", "D", "A", ...] 
        for _ in range(number_of_subgroups):
            letter = random.choice(self.student_letter_list)
            student_partition_list.append(letter)        
        
        # store the list in the self.partition attribute
        self.partition = student_partition_list
        
        return self.partition

    
    def load_partition(self, partition):
        """
        A method to load a partition into memory given a string representation
        
        Parameters
        ----------
        partition:
            a list of the form ["A", "C", "D", ...]
        
        """     
        student_partition_list = []

        for student_partition_assignment in partition:
            student_partition_list.append(student_partition_assignment)

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
    
    student_letter_list : list
            either ["A", "B"] or ["A", "B", "C", "D"]
    
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
        self.student_letter_list = individual_partition_obj.student_letter_list

    def generate_individual(self):
        """
        A method to generate a random partition, ex: ["A", "A", "C", "B", "D", "A", ...]
        
        Parameters
        ----------
        None
        """
        
        return self.individual_partition_obj.generate_partition()


    def load_population(self, population):
        """
        A method to load a population into memory given a string representation
        
        Parameters
        ----------
        population:
            a list of partitions, where each partition is represented as a list ["A", "C", "D", ...]
            Example: [ ["A", "C", "D"], ["B", "B", "A"], ["C", "A", "A"] ]
        
        """        
        
        self.population = []
        for partition in population:
            individual = self.individual_partition_obj.load_partition(partition)
            self.population.append(individual)


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
        self.sorted_scored_population = []

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
    next_generation:
        the next generation of individuals as determined by the algorithm, 
        this is a list in the form [(score1, population1), (score2, population2), ...]
    number_of_partitions: int
        inherited from the Population class
    student_letter_list : list
        either ["A", "B"] or ["A", "B", "C", "D"]   
        
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
        self.student_letter_list = population_obj.student_letter_list
        
    def mutate(self, individual_partition):
        """
        A method to mutate children based on a specified mutation rate
        
        Source: https://en.wikipedia.org/wiki/Mutation_(genetic_algorithm)
        
        Parameters
        ----------
        individual_partition : list
            a list in the form ["A", "A", "B", "D", "A", "C", "B", "C", ...]
        """        
                
        # the mutated partition
        new_partition = []
        
        # for each letter in your ["A", "A", "B", "D", "A", "C", "B", "C", ...]:
        for letter in individual_partition: 
            
            # generate a random number between 0 and 1 
            # (rolling the dice to see if we are a winner)
            check_mutate = random.random() 
            
            # if we win our "dice roll", then mutate:
            if check_mutate < self.mutation_rate:
                # subtract the letter from STUDENT_LETTER_LIST
                # for example, if letter = "A" and 
                # STUDENT_LETTER_LIST = ["A","B","C","D"], then
                # intersected_list = ["B","C","D"]
                intersected_list = [element for element in self.student_letter_list if element is not letter]
                
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


        # one pair of parents produce one pair of children
        child1, child2 = get_children_pair(parent1, parent2)


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


        # for the tournament selection when crossing two partitions within an island,
        # the number of representatives to use. the below seems to work well in practice.
        number_of_tournament_reps_per_population = scored_population_length //10


        # select the two parents using tournament selection
        # the number 4 is somewhat arbitrary, but seems to work well in practice
        parent1_index = tournament_winner_index(scored_population_length, number_of_tournament_reps_per_population)
        parent1 = list(scored_population[parent1_index])
        
        parent2_index = tournament_winner_index(scored_population_length, number_of_tournament_reps_per_population)
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
        scored_next_generation = self.population_obj.population_fitness()
        
        # after scoring, assign this to self.next_generation
        # self.next_generation is in the form [(score1, partition1), (score2, partition2), ...]
        self.next_generation = scored_next_generation
        
        return self.population_obj.sorted_scored_population

def run_era(student_csv_path, 
            required_subgroups_csv_path, 
            preferred_subgroups_csv_path, 
            number_of_partitions, 
            half_class_maximum, 
            quarter_class_maximum, 
            pop_size, 
            rate_of_mutation, 
            max_era, 
            max_gen, 
            out_queue, 
            in_queue):
    """
    Repeat the Genetic Algorithm based on a specified number of generations (or time limit)
                
    Parameters
    ----------
    student_csv_path : str
        the location of the input.csv with student schedule data
    required_subgroups_csv_path : str
        the location of the input.csv with required subgrouping data
    preferred_subgroups_csv_path : str
        the location of the input.csv with preferred subgrouping data
    number_of_partitions: int
        the number of partitions to group students into
        2 for an A/B partition
        4 for an A/B/C/D partition
        Note: Other values are not implemented
    pop_size: int
        the size of the population in the genetic algorithm
    rate_of_mutation: float
        the mutation rate in the genetic algorithm
    max_era: int
        the number of eras to run
    max_gen: int
        the number of generations per era to run the algorithm
    out_queue: multiprocessing.Queue()
        threadsafe outbound queue, used to report final population to main()
    in_queue: multiprocessing.Queue()
        threadsafe inbound queue, used to receive crossbred population from main()
    """     
    
    # this function is run by child processes that main() launches, so grab the process ID for logging purposes
    process_ID_as_string = str(os.getpid())

    # initializer the timer to 0
    timer_total = 0
    
    # start the timer
    start_timer = time.perf_counter()
    
    generation_number = 1
    era_number = 0
    
    # instantiate the Schedule object
    load_schedule = Schedule(number_of_partitions, half_class_maximum, quarter_class_maximum)
    
    # load school data into the Schedule object
    load_schedule.students_from_csv(student_csv_path)
    
    # load required subgroups into the Schedule object
    load_schedule.subgroups_from_csv(required_subgroups_csv_path, "required")    
    
    # load preferred subgroups into the Schedule object
    load_schedule.subgroups_from_csv(preferred_subgroups_csv_path, "preferred")
    
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
    # (This includes the initial CSV load, so it will be a bit longer than the general case)
    # print("Benchmark result = " + str(end_timer - start_timer))

    # Concatenate a string to report progress:
    progress_string = "PID(" + process_ID_as_string + "):"
    progress_string += "Generation = "
    progress_string += str(generation_number)
    progress_string += ", Fitness = "
    progress_string += str(previous_population[0][0][0])
    progress_string += ", In Compliance = "
    progress_string += str(previous_population[0][0][2])
    progress_string += " out of "
    progress_string += str(previous_population[0][0][-1])   
    progress_string += ", elapsed time so far this era (sec) = " + str(timer_total)
    
    # Print progress & write to the progress log:
    print(progress_string)

    progress_file = IO_DIRECTORY / 'progress_log.txt'    
    with open(progress_file, 'w') as file:
        file.write(progress_string)
        file.write("\n")   

    # keep repeating this process until the maximum number
    # of generations or the time limit has been reached
    while generation_number < max_gen:
        
        # same process as above
        start_timer = time.perf_counter()
        
        generation_number += 1
        
        population.sorted_scored_population = previous_population
        current_generation = GeneticAlgorithm(population, generation_number, rate_of_mutation)
        current_generation.generate_next_generation()
        previous_population = current_generation.next_generation
        
        end_timer = time.perf_counter()
        timer_total += end_timer - start_timer

        # Uncomment below to track how long this took:
        # (This is the general case WITHOUT initial CSV load)
        # print("Benchmark result = " + str(end_timer - start_timer))
        
        progress_string = "PID[" + process_ID_as_string + "]: "
        progress_string += "Generation = "
        progress_string += str(generation_number)
        progress_string += ", Fitness = "
        progress_string += str(previous_population[0][0][0])
        progress_string += ", In Compliance = "
        progress_string += str(previous_population[0][0][2])
        progress_string += " out of "
        progress_string += str(previous_population[0][0][-1])
        progress_string += ", elapsed time so far this era (sec) = " + str(timer_total)
        
        print(progress_string)

        with open(progress_file, 'a') as file:
            file.write(progress_string)
            file.write("\n") 
        

    """
    Now that this era is done, this island process must send its findings back to main(). We can
    represent our findings as a sorted list: [partition1, partition2, ...], where partition1 is the
    best, partition2 is second best, etc.
    
    Due to some limitations of Python interprocess communication, we represent each partition as a
    list of letters rather than an actual IndividualPartition() object.
    
        Example representation:    [ ["A", "C", "B"], ["B", "A", "C"], ["C", 'C", "A"], ...]

    This would mean that, on this island, the most successful partition we found was ["A", "C", "B"]; the
    second most successful partition we found was ["B", "A", "C"]; and so on.
    """
    era_number += 1
    result_population = []

    for item in previous_population:
        result_population.append(item[1])


    out_queue.put(result_population)


    # at the end of an era, write a student assignment report
    # and a course-by-course analysis report
    final_partition = previous_population[0][1]
    load_schedule.load_partition(final_partition)
    load_schedule.write_student_assignments()
    load_schedule.write_course_analysis()


    """
    This island process just finished its first era, after having read in the CSV file
    and seeding itself with a random partition.

    Now, we enter a second phase: we simply wait for main() to send us a new crossbred
    population via in_queue, then load that population into our genetic algorithm,
    and compute another era. And so on.
    """
    while era_number < max_era:
        # This is a blocking call until we receive a crossbred population from main()
        crossbred_population = in_queue.get()

        # Now that we've received a crossbred population, we start a new era
        generation_number = 1

        # Start timers for logging
        timer_total = 0
        start_timer = time.perf_counter()

        # Load the received population into our in-memory population object
        population.load_population(crossbred_population)

        # score this initial population
        population.population_fitness()
        
        # instantiate the GeneticAlgorithm object
        first_generation = GeneticAlgorithm(population, generation_number, rate_of_mutation)
        
        # generate Generation #2
        first_generation.generate_next_generation()
        previous_population = first_generation.next_generation
        

        # track the time this process took
        end_timer = time.perf_counter()
        timer_total += end_timer - start_timer

        

        # Concatenate a string to report progress:
        progress_string = "PID[" + process_ID_as_string + "]: "
        progress_string += "Generation = "
        progress_string += str(generation_number)
        progress_string += ", Fitness = "
        progress_string += str(previous_population[0][0][0])
        progress_string += ", In Compliance = "
        progress_string += str(previous_population[0][0][2])
        progress_string += " out of "
        progress_string += str(previous_population[0][0][-1])   
        progress_string += ", elapsed time so far this era (sec) = " + str(timer_total)
        
        # Print progress & write to the progress log:
        print(progress_string)

        progress_file = IO_DIRECTORY / 'progress_log.txt'    
        with open(progress_file, 'w') as file:
            file.write(progress_string)
            file.write("\n") 

        # keep repeating this process until the maximum number
        # of generations or the time limit has been reached
        while generation_number < max_gen:
            
            # same process as above
            start_timer = time.perf_counter()

            generation_number += 1
            
            population.sorted_scored_population = previous_population
            current_generation = GeneticAlgorithm(population, generation_number, rate_of_mutation)
            current_generation.generate_next_generation()
            previous_population = current_generation.next_generation
            
            end_timer = time.perf_counter()
            timer_total += end_timer - start_timer
            
                        
            progress_string = "PID[" + process_ID_as_string + "]: "
            progress_string += "Generation = "
            progress_string += str(generation_number)
            progress_string += ", Fitness = "
            progress_string += str(previous_population[0][0][0])
            progress_string += ", In Compliance = "
            progress_string += str(previous_population[0][0][2])
            progress_string += " out of "
            progress_string += str(previous_population[0][0][-1])
            progress_string += ", elapsed time so far this era (sec) = " + str(timer_total)
            
            print(progress_string)

            with open(progress_file, 'a') as file:
                file.write(progress_string)
                file.write("\n") 

            
        # Send population back to main()
        result_population = []

        for item in previous_population:
            result_population.append(item[1])


        out_queue.put(result_population)


        # at the end of an era, write a student assignment report
        # and a course-by-course analysis report
        final_partition = previous_population[0][1]
        load_schedule.load_partition(final_partition)
        load_schedule.write_student_assignments()
        load_schedule.write_course_analysis()

        # now we go back to the start of "while True" loop, where we wait
        # for main() to send the crossbred population back to us
        era_number += 1


    # We ran all of the eras we were supposed to run, we can exit now
    return 0
            


def get_crossed_children(population1, population2, num_children, num_tournament_reps):
    """
    Helper function used by crossbreed_islands. Given two populations, this method
    uses tournament selection to choose a parent from each population. These two
    parents then create a pair of children. This process is repeated until num_children
    children are produced.

    Returns a list of children, where each child is a partition
    (so it's returning a list of list of strings)

    THIS LOGIC WILL BE CHANGED QUITE A BIT IN THE NEXT CHECK IN,
    TRYING TO KEEP THIS CHECK IN TO JUST THE MULTIPROCESSING STUFF

    Parameters
    ----------
    population1:
        represents the population of an island: [ ["A", "B", ...], ["B", "C", ...], ... ]
        parent1 will be selected from this
    population2:
        represents the population of an island: [ ["A", "B", ...], ["B", "C", ...], ... ]
        parent2 will be selected from this
    num_children: int
        number of children to generate and return
    num_tournament_reps: int
        for the tournament selection to select parents, the number of representatives to use
    """  


    # size of each population
    population_size = len(population1)

    # list to store the children
    crossed_children_list = []
    
    for _ in range(num_children//2):
        # select the two parents using tournament selection
        # the number 4 is somewhat arbitrary, but seems to work well in practice
        parent1_index = tournament_winner_index(population_size, num_tournament_reps)
        parent1 = population1[parent1_index]
        
        parent2_index = tournament_winner_index(population_size, num_tournament_reps)
        parent2 = population2[parent2_index]

        
        # length of a partition
        genome_length = len(parent1)
        



        # a pair of parents generates a pair of children
        child1, child2 = get_children_pair(parent1, parent2)

        # add the pair of children to the output list
        crossed_children_list.append(child1)
        crossed_children_list.append(child2)


        # We are generating children in pairs, if we accidentally
        # add one child too many to self.next_generation, take off 
        # the extra child 
        if len(crossed_children_list) > num_children: 
            crossed_children_list = crossed_children_list[0:-1]

    return crossed_children_list



def get_children_pair(parent1, parent2):
    """
    a given pair of parents create 2 new children:
        1. child1 starts off as a clone of parent1, just as child2 starts off as a clone of parent2.
        2. these 2 clones then have an opportunity to swap some genes (individual student letter assignments).
           this happens by selecting a random [relatively small] subset of itself (i.e. a set of indices), and 
           having child1 and child2 swap their letters at these indices.

           the idea is that each parent might have found a successful schedule of a small "chunk" of students
           that the other parent did not find yet (or was not successful in that overall environment), and this
           is a way to inject those small "local" changes (local in the sense that it is an improvement that can
           be made to a small cohort of students that doesn't really affect those outside of this cohort).
        3. so whenever we take a parent from island1 to cross it with a parent from island2, the original population
           [of island1] gets 2 children: one that is a near-clone of parent1 (and island1 native), and another one
           that is a near-clone of parent2 (a foreigner from island2)

    ****

    I HAVE NO IDEA IF THIS "SHOULD" WORK OR WHAT... it's just what I came up with from "thinking about it",
    and it seems to yield some improvements in my testing. if you find an improvement, that's even better!


    Parameters
    ----------
    parent1:
        list of letters representing parent1 (the partition)

    parent2:
        list of letters representing parent1 (the partition)

    """    


    genome_length = min(len(parent1), len(parent2))


    # child1 and child2 start off as clones of their respective parents
    child1 = parent1[:]
    child2 = parent2[:]


    # size of cohort to inject, i.e. number of letters to replace in the partition
    # this is purely based on [what seems right to me] based on some limited experimentation
    # far from finalized, please feel free to play around with the parameters
    # some small number (such as between 10 and 40) seems to work best
    injection_size = random.randint(10,30)

    # choose injection_size random indexes which will get the other parent's genes
    for _ in range(injection_size):
        # choose 
        rand_index = random.randint(0, genome_length-1)
        temp = child1[rand_index]
        child1[rand_index] = child2[rand_index]
        child2[rand_index] = temp

    return child1, child2


def tournament_winner_index(array_length, num_reps):
    """
    Helper function. Uses tournament selection with num_reps representatives to 
    select an index for an array of length array_length.

    Source (tournament selection): https://en.wikipedia.org/wiki/Tournament_selection

    Parameters
    ----------
    array_length: int
        the length of the array for which we are using tournament selection

    num_reps: int
        number of representatives to use for tournament selection

    """    
    
    # our population is stored in descending order, so start off by assuming
    # we have the worst possible index, then we get num_reps tries
    # to improve upon (i.e. to minimize) this value
    cur_winner = array_length

    for _ in range(num_reps):
        cur_winner = min(cur_winner, random.randint(0, array_length-1))

    return cur_winner




def crossbreed_islands(island_populations, number_of_islands, number_of_tournament_reps_per_island):
    """
    Helper function for crossbreeding across different island populations.
    Returns the list containing the crossbred populations.

    Parameters
    ----------
    island_populations:
        a list of island populations of the form [population1, population2, ...]
        each population is of the form [partition1, partition2, ...]
        each partition is of the form ["A", "C", ...]

        putting all this together, island_populations is of the form:
        [ [["A", "B", ...], ["B", "C", ...], ...],      <-- population1
          [["C", "B", ...], ["A", "A", ...], ...],      <-- population2
          ...                                    ,      <-- population3
          ...
        ]    

    """    
    
    # each population keeps the top 25% elites
    num_elites = len(island_populations[0])//4

    # an empty list for each of the crossed populations 
    crossed_populations = [[] for _ in range(number_of_islands)]
    
    # populate the 25% elites onto each island:
    for i in range(number_of_islands):
        crossed_pop = crossed_populations[i]
        orig_pop = island_populations[i]
        crossed_pop.extend([item for item in orig_pop[0:num_elites]])
    
    # for each island population, the remaining 75% is composed of 
    # [crossing with each of the other (number_of_islands - 1) islands].

    # divide the remaining number of partitions as evenly as possible into
    # (1/((number_of_islands - 1)))ths
    
    # most groups will be of this size:
    num_children = (len(island_populations[0]) - num_elites)//(number_of_islands - 1)
    
    # the last group will be composed of whatever space is left over:
    remainder = len(island_populations[0]) - num_elites - (num_children)*(number_of_islands - 2)

    # for each island:
    for i in range(number_of_islands):
        # the crossed population (that currently only has elites)
        crossed_pop = crossed_populations[i]
        
        # the first population to cross with: 
        first_pop = island_populations[i]
        
        # the indices of the remaining populations to cross with:
        other_indices = [n for n in range(number_of_islands)]
        other_indices.remove(i)
        
        # for each index (except the last):
        for index in other_indices[:-1]:
            # get the second population for crossing
            second_pop = island_populations[index]
            
            # cross the two islands and add the children to cross_pop 
            # (the number of children added will = num_children)
            crossed_pop.extend(get_crossed_children(first_pop, second_pop, num_children, number_of_tournament_reps_per_island))
        
        # cross with the last island and add the children to cross_pop
        # (this time, the number of children added will = remainder)
        crossed_pop.extend(get_crossed_children(first_pop, island_populations[-1], remainder, number_of_tournament_reps_per_island))

    # return the list of crossed populations
    return crossed_populations




def main():
    """
    In order to take advantage of multiple cores, main() works as follows:
        1. Launch NUMBER_OF_PROCESSES processes, each of which runs an instance of the run_era() function.
           You can think of this as the genetic algorithm working on N separate islands.
        2. After running the genetic algorithm for NUMBER_OF_GENERATIONS_PER_ERA generations, these processes
           each report their population back to main().
        3. We have just completed an "era". We now start the next era by crossbreeding these populations
           and then feeding the crossbred population back to each island (process), so that each island can
           go off and run the genetic algorithm for another era in isolation before reporting back, etc.
    """
    # if you open a .csv report in Microsoft Excel and leave it open,
    # this program will throw a PermissionError when it tries to write
    # the new .csv report
    #
    # this warning is to remind you to close these .csv files before this
    # happens
    #
    warnings.warn("To avoid permission errors, close any output files you may have left open from previous runs.")

    # The "island" processes report back to main() by putting their population into this threadsafe queue
    island_population_queue = multiprocessing.Queue()

    # main() can then send the crossbred populations back to the "island" processes via this threadsafe queue
    crossbred_population_queue = multiprocessing.Queue()

    # store the processes that we launch in a list
    island_processes = []

    # instantiate NUMBER_OF_PROCESSES island processes, each of which will execute run_era()
    for _ in range(0, NUMBER_OF_PROCESSES):
        p = multiprocessing.Process(target=run_era, args=(INPUT_CSV_FILENAME,
                                                          REQUIRED_SUBGROUP_CSV_FILENAME,
                                                          PREFERRED_SUBGROUP_CSV_FILENAME,
                                                          NUMBER_OF_PARTITIONS,
                                                          HALF_CLASS_MAXIMUM,
                                                          QUARTER_CLASS_MAXIMUM,
                                                          POPULATION_SIZE,
                                                          MUTATION_RATE,
                                                          NUMBER_OF_ERAS,
                                                          NUMBER_OF_GENERATIONS_PER_ERA,
                                                          island_population_queue,
                                                          crossbred_population_queue))
        island_processes.append(p)


    # start the processes
    for p in island_processes:
        p.start()



    # timers for logging
    start_timer = end_timer = total_time = 0
    
    # number of eras we've completed
    era_number = 0


    # one iteration through this loop represents one era
    while total_time < 60*TIME_LIMIT and era_number < NUMBER_OF_ERAS:
        # we will time how long this era takes us
        start_timer = time.perf_counter()

        # each island will send us their population - store all of them in this list
        island_populations = []

        # get() is blocking, so the main() process will spend most of its
        # time waiting here for all of the islands to report back
        for i in range(NUMBER_OF_PROCESSES):
            island_populations.append(island_population_queue.get())


        # now that we have a population from each island, crossbreed
        # both the input (island_populations) and the output (crossed_populations)
        # is represented as a list of populations
        crossed_populations = crossbreed_islands(island_populations, NUMBER_OF_PROCESSES, NUMBER_OF_TOURNAMENT_REPS_PER_ISLAND)


        # send this crossed population back to the island process via crossbred_population_queue
        # (each island process is constantly checking this queue for a crossbred population,
        #  and once it is able to pop one off, starts computing the new era using that initial population)
        for item in crossed_populations:
            crossbred_population_queue.put(item)


        # we're done with this era
        era_number += 1

        # log time elapsed
        end_timer = time.perf_counter()
        total_time += (end_timer - start_timer)
        print("Just completed era #" + str(era_number) + " in " + str(round(end_timer - start_timer, 3)) + "sec")
        print("Total elapsed time: " + str(round(total_time/60, 2)) + " min")



    # wait for all processes to exit
    for p in island_processes:
        p.join()




if __name__ == "__main__":
    main()
















