# Student Partition Optimization Tool for Schools (SPOTS)
State governments and public health agencies have begun recommending that schools implement "Physically Distanced Learning," with a student/teacher ratio of 10/1 or fewer in each classroom. At most schools, this will require rotating groups of students into the school building while other students stay home and learn remotely. This project aims to help schools assign students to an A/B/C/D group in a manner that allows physical distancing in as many classrooms as possible. 

Video introduction: https://youtu.be/XJFvY4-FCSc

## Prerequisites

Python 3.8 (https://www.python.org/downloads/)

### Getting Started (Example Data)

To try this program with the provided example data, you only need to make a single change in SPOTS.py. At the top of the file, locate the constant named IO_DIRECTORY and indicate the path for example.csv. This will also be where the final reports will be located (student_assignments.csv and course_analysis.csv).

		NUMBER_OF_PARTITIONS = 4 # number of groups to partition students into (only 2 and 4 are implemented)
		MUTATION_RATE = 0.015 # recommended range: between 0.01 and 0.05, current default = 0.015
		POPULATION_SIZE = 200 # recommended range: between 100 and 1,000, current default = 200
		NUMBER_OF_GENERATIONS = 100000 # recommended range: at least 10,000, current default = 100000
		**IO_DIRECTORY = "C:\\YOUR_DIRECTORY_HERE" # location of input .csv file, for example "C:\\Users\\jsmith\\Desktop\\"**
		INPUT_CSV_FILENAME = "example.csv" # filename of .csv file
		TIME_LIMIT = 60*8 # time measured in minutes, current default = 480 min (8 hr)

After you have the program working with example data, you can try data from your own school. 

### Getting Started (Your School's Data)

This program uses a genetic algorithm to optimize a partition of students. In order to evaluate the fitness of a given partition, the algorithm must check the partition against your school's master schedule. You will need to generate a .csv file with the following fields:
     
        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
		
The three most important columns in this .csv file are STUDENT_ID, ROOM_NUMBER, and PERIOD: these cannot be omitted. The algorithm uniquely identifies individual students using STUDENT_ID. Courses within a school building are uniquely identified using the pair (ROOM_NUMBER, PERIOD). All other columns can be modified or removed (and new columsn can be added) with proper modifications to the program.

This .csv file should have an entry for each student course enrollment. For example, if John Smith is taking 7 classes, then John Smith should have 7 rows in the .csv file:

        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
        John, Smith, William, 000281871, Math435-01,    ALGEBRA 2/TRIG,2381878, ROOM 255,    PERIOD 1
        John, Smith, William, 000281871, Eng402-01,     ADV BRITISH LIT,342243, ROOM 211,    PERIOD 2
        John, Smith, William, 000281871, Hist424-01,    AP WORLD HIST,50122439, ROOM 166,    PERIOD 3
        John, Smith, William, 000281871, Chem419-01,    AP CHEMISTRY,544433238, ROOM 200,    PERIOD 5
        John, Smith, William, 000281871, Band300-01,    MARCHING BAND,40391878, ROOM 003,    PERIOD 6
        John, Smith, William, 000281871, Germ461-01,    AP GERMAN LANG,1943981, ROOM 214,    PERIOD 7
        John, Smith, William, 000281871, Gym400-01,     ADVENTURE EDUCATION,23, ROOM GYM,    PERIOD 8

Once you have generated this .csv file, you will have to edit SPOTS.py to indicate the path for your .csv file (as well as a few other parameters that you can modify if desired). These are all located near the top of SPOTS.py:

		**NUMBER_OF_PARTITIONS = 4 # number of groups to partition students into (only 2 and 4 are implemented)**
		MUTATION_RATE = 0.015 # recommended range: between 0.01 and 0.05, current default = 0.015
		POPULATION_SIZE = 200 # recommended range: between 100 and 1,000, current default = 200
		NUMBER_OF_GENERATIONS = 100000 # recommended range: at least 10,000, current default = 100000
		**IO_DIRECTORY = "C:\\YOUR_DIRECTORY_HERE" # location of input .csv file, for example "C:\\Users\\jsmith\\Desktop\\"**
		INPUT_CSV_FILENAME = "example.csv" # filename of .csv file
		TIME_LIMIT = 60*8 # time measured in minutes, current default = 480 min (8 hr)

If your school is implementing an A/B partition, set NUMBER_OF_PARTITIONS = 2. For an A/B/C/D partition, leave the default value of NUMBER_OF_PARTITIONS = 4. You will have to add to this project for a partition size other than 2 or 4. 

### Advanced Users

If you are familiar with genetic algorithms (or would just like to experiment), you can try changing the default values for MUTATION_RATE, POPULATION_SIZE, and NUMBER_OF_GENERATIONS. 

		NUMBER_OF_PARTITIONS = 4 # number of groups to partition students into (only 2 and 4 are implemented)
		**MUTATION_RATE = 0.015 # recommended range: between 0.01 and 0.05, current default = 0.015**
		**POPULATION_SIZE = 200 # recommended range: between 100 and 1,000, current default = 200**
		**NUMBER_OF_GENERATIONS = 100000 # recommended range: at least 10,000, current default = 100000**
		IO_DIRECTORY = "C:\\YOUR_DIRECTORY_HERE" # location of input .csv file, for example "C:\\Users\\jsmith\\Desktop\\"
		INPUT_CSV_FILENAME = "example.csv" # filename of .csv file
		TIME_LIMIT = 60*8 # time measured in minutes, current default = 480 min (8 hr)

It may be possible to modify these parameters to obtain better results. Please email studentpartitionoptimizer@gmail.com if you have parameters you would like to suggest for new default values. 

Finally, a genetic algorithm is only as good as its fitness function. You may choose to adapt Schedule.fitness_score() to your school's needs (or possibly to obtain optimal results in less time). Please email studentpartitionoptimizer@gmail.com if you have a suggested change to Schedule.fitness_score(). 

### Final Output 

As the algorithm runs, it will append results to the file progress_log.txt. You can check this file to watch the progress of the algorithm. Because the first generation in this algorithm assigns student to A/B/C/D groups randomly, early generations will have a low fitness score and a limited number of courses that are rated as "In Compliance." These early generations are similar to the quality of partitions that a human could generate by hand. You should notice a significant jump in the number of "In Compliance" courses for later generations.   

This program will also generate two final reports at the end of the algorithm: student_assignments.csv and course_analysis.csv. The student_assignments report is self-explanatory:

		Student ID, Last, First, Middle, Letter
		0291817791, Abel, Niels, Henrik, D
		0999023822, John, Mikey, Norman, A

It is just a list of students and the A/B/C/D groups to which they have been assigned. The course_analysis report is meant to analyze the final results of these particular A/B/C/D assignments. You may consider sorting by "In Compliance" to locate all courses that have been reported as "No." 

Some of these courses will not be "In Compliance" because they are simply too large. This program defines a course as "In Compliance" if it has no more than 9 students to the A-group, 9 students to the B-group, 9 students to the C-group, and 9 students to the D-group. This is impossible if the course has 40 students in it. 

Other courses will not be "In Compliance" because they have an imbalance in the size of the A/B/C/D groups that is too large. You can identify these courses by looking a large value for "Max Deviation" (as well as "In Compliance" = "No"). Sometimes, it will be possible to get some of these course to be "In Compliance" by running the algorithm longer (or running on a few machines and selecting the best results). However, schedule optimization is well known to be a difficult problem, and it is not realistic to expect 100% of courses achieving a rating of "In Compliance." 

## Author

* **Christopher Grattoni** - *Initial work* - [NFLtheorem](https://github.com/NFLtheorem/partitionoptimizer)

See also the list of [contributors](https://github.com/NFLtheorem/partitionoptimizer/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks, brother.

