*New in this Version:* Support for assigning siblings to the same letter group.

# Student Partition Optimization Tool for Schools (SPOTS)
State governments and public health agencies have begun recommending that schools implement "Physically Distanced Learning," with a student/teacher ratio of 10/1 or fewer in each classroom. At most schools, this will require rotating groups of students into the school building while other students stay home and learn remotely. This project aims to help schools assign students to an A/B/C/D group in a manner that allows physical distancing in as many classrooms as possible. 

Video introduction: https://youtu.be/XJFvY4-FCSc

### What Does This Program Do?

The Student Partition Optimization Tool for Schools uses a genetic algorithm to assign each student at your school to a subgroup in a way that facilitates physical distancing in as many classrooms as possible. This program supports partitioning students into 2 subgroups (an A/B partition) or 4 subgroups (an A/B/C/D partition). For an A/B/C/D partition, a course at your school will be classified as "In Compliance" if it meets the following criteria:

1. No more than 9 students in any one letter group, more explicitly:
   - No more than 9 A's
   - No more than 9 B's
   - No more than 9 C's
   - No more than 9 D's
2. No more than 15 students when combining the A- and B-groups
3. No more than 15 students when combining the C- and D-groups

This allows schools some flexibility if they have to rotate students in and out of the building. If a school can have no more than 10 people in a classroom (9 students and 1 teacher), then the school can rotate through the A/B/C/D groups one at a time. If a school needs to run each classroom at approximately 50% capacity, they can bring in the A- and B-groups together, and then bring in the C- and D-groups together. 

For courses that are not initially "In Compliance," the algorithm attempts to balance the distribution of students in the A/B/C/D groups, as well as the distribution of students in the (A+B) and (C+D) groups. 

If a school has a different set of requirements than a maximum of 9 students in A/B/C/D groups and 15 students in (A+B) and (C+D) groups, then the fitness function in SPOTS.py can easily be modified to accommodate this. 

**Important:** A genetic algorithm is an optimization technique whose results improve with additional computation. You may want to let this program work for 8 hours or more to obtain desirable results.

## Prerequisites

Python 3.8 (https://www.python.org/downloads/)

### Getting Started (Example Data)

To try this program with the provided example data, you only need to make a single change to SPOTS.py. At the top of the file, locate the constant named IO_DIRECTORY and indicate the path for example.csv. This will also be where the final reports will be located (student_assignments.csv and course_analysis.csv).

		# location of input .csv file (example: "C:\\Users\\jsmith\\Desktop\\")
		IO_DIRECTORY = "C:\\Users\\jsmith\\Documents\\GitHub\\partitionoptimizer\\" 
		
After you have the program working with example data, you can try data from your own school. 

### Getting Started (Your School's Data)

This program uses a genetic algorithm to optimize a partition of students. In order to evaluate the fitness of a given partition, the algorithm must check the partition against your school's master schedule. You will need to generate a .csv file with the following fields:
     
        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
		
The three most important columns in this .csv file are STUDENT_ID, ROOM_NUMBER, and PERIOD: these cannot be omitted. The algorithm uniquely identifies individual students using STUDENT_ID. Courses within a school building are uniquely identified using the pair (ROOM_NUMBER, PERIOD). All other columns can be modified or removed (and new columns can be added) with proper modifications to the program.

This .csv file should have an entry for each student course enrollment. For example, if John Smith is taking 7 classes, then John Smith should have 7 rows in the .csv file:

        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
        John, Smith, William, 000281871, Math435-01,    ALGEBRA 2/TRIG,2381878, ROOM 255,    PERIOD 1
        John, Smith, William, 000281871, Eng402-01,     ADV BRITISH LIT,342243, ROOM 211,    PERIOD 2
        John, Smith, William, 000281871, Hist424-01,    AP WORLD HIST,50122439, ROOM 166,    PERIOD 3
        John, Smith, William, 000281871, Chem419-01,    AP CHEMISTRY,544433238, ROOM 200,    PERIOD 5
        John, Smith, William, 000281871, Band300-01,    MARCHING BAND,40391878, ROOM 003,    PERIOD 6
        John, Smith, William, 000281871, Germ461-01,    AP GERMAN LANG,1943981, ROOM 214,    PERIOD 7
        John, Smith, William, 000281871, Gym400-01,     ADVENTURE EDUCATION,23, ROOM GYM,    PERIOD 8

Once you have generated this .csv file, you will have to edit SPOTS.py to indicate the name of your .csv file so that it does not point at the example data anymore. Replace "example_student_data.csv" with the name of your specific file:

		# filename of .csv file with student schedule data (default = "example.csv) 
		INPUT_CSV_FILENAME = "example_student_data.csv" 
		
Next, if your school is implementing an A/B partition, set NUMBER_OF_PARTITIONS = 2. For an A/B/C/D partition, leave the default value of NUMBER_OF_PARTITIONS = 4. You will have to add to this project for a partition size other than 2 or 4:

		# number of groups to partition students into (only 2 and 4 are implemented)
		NUMBER_OF_PARTITIONS = 4

You can also modify the desired size of the letter partition in each classroom. By default, the program will try to assign no more than 9 students of each letter (A/B/C/D) and 15 students in the paired groups ((A + B) and (C + D)). Here is where to make these changes:

		# max size of a partition when dividing students into two subgroups (default = 15) 
		HALF_CLASS_MAXIMUM = 15 

		# max size of a partition when dividing students into four subgroups (default = 9)
		QUARTER_CLASS_MAXIMUM = 9

After making these changes, you are ready to try the program out on real data. 
		
## Student Subgroup Support

There are many reasons why schools may want the ability to guarantee that a certain students receive the same letter assignment as other students. The most common case is likely to be to assign siblings to the same letter group. As a result, this program now supports "student subgroups." There are two types of subgroups that this program supports:

*Required* subgroups: The program will enforce that these subgroups be preserved. That is, if Student1 and Student2 are in a subgroup, they _must_ be assigned to the same subgroup. 

*Preferred* subgroups: The program will show a preference for preserving these subgroups, but it will prioritize physical distancing requirements over subgroup integrity. 

### Required Student Subgrouping Example

All you need to try out Student Subgroups is a .csv file with two columns of Student ID numbers:

		ID Num 1, ID Num 2
        09281381, 20383882
        42074738, 87172918
        09281381, 63471199

Look at the first row "09281381, 20383882". Suppose John Smith has the ID number "09281381" and Mary Smith has the ID number "20383882". This row indicates that John Smith and Mary Smith must be assigned to the same letter group. We will not know what particular letter they will be assigned to until the program runs, but we are guaranteed that these two students will share a letter assignment.

In the second row, we have a new set of students who must be assigned to the same group. Suppose James Taylor has the ID number "42074738" and Victor Washington has the ID number "87172918". Then James and Victor must be assigned to the same letter group. 

In the third row, we see that John Smith is back with his ID number of "09281381". Suppose that the second ID number, "63471199", corresponds to William Smith. Now we have a three person subgroup because John, Mary, and William must be assigned to the same letter group. 

In order to try this out with example data, try changing REQUIRED_SUBGROUP_CSV_FILENAME from None to "example_subgroups.csv":

		# filename of .csv file with required student subgrouping data 
		# example data = "example_subgroups.csv"
		# if not applicable, use None
		REQUIRED_SUBGROUP_CSV_FILENAME = None # also try "example_subgroups.csv" 

After you try this out with example data, you can try your own .csv with required student pairings. 

*Warning:* Schools should be wary about assigning too many students to subgroups. This program is more effective when the algorithm can adequately explore its potential solution space. Every time a student is placed into a subgroup, this is placing a limit on the quality of the results the algorithm can produce. In my initial testing, it seems like good results can still be produced when grouping together siblings, but I have not tested what happens with much larger subgrouping restrictions.  

### Advanced Users

If you are familiar with genetic algorithms (or would just like to experiment), you can try changing the default values for MUTATION_RATE, POPULATION_SIZE, and NUMBER_OF_GENERATIONS. You can also set a time limit for how long the algorithm runs: 

		# recommended range: between 0.01 and 0.05 (default = 0.015)
		MUTATION_RATE = 0.015 

		# recommended range: between 100 and 1,000 (default = 200)
		POPULATION_SIZE = 200 

		# recommended range: at least 10,000 (default = 100000)
		NUMBER_OF_GENERATIONS = 100000 

		# time measured in minutes (default = 480 min or 8 hr)
		TIME_LIMIT = 60*8

It may be possible to modify these parameters to obtain better results. Please email studentpartitionoptimizer@gmail.com if you have parameters you would like to suggest for new default values. 

Finally, a genetic algorithm is only as good as its fitness function. If you really want to experiment, find the method Schedule.fitness_score() and make modificatins. These changes can either be tailored to your school's needs, or you might make a modification to obtain optimal results in less time. Please email studentpartitionoptimizer@gmail.com if you have a suggested change to Schedule.fitness_score(). 

### Final Output 

As the algorithm runs, it will append results to the file progress_log.txt. You can check this file to watch the progress of the algorithm. Because the first generation in this algorithm assigns students to A/B/C/D groups randomly, early generations will have a low fitness score and a limited number of courses that are rated as "In Compliance." These early generations are similar to the quality of partitions that a human could generate by hand. You should notice a significant jump in the number of "In Compliance" courses for later generations.   

This program will also generate two final reports at the end of the algorithm: student_assignments.csv and course_analysis.csv. The student_assignments report is self-explanatory:

		Student ID, Last, First, Middle, Letter
		0291817791, Abel, Niels, Henrik, D
		0999023822, John, Mikey, Norman, A

It is just a list of students and the A/B/C/D groups to which they have been assigned. The course_analysis report is meant to analyze the final results of these particular A/B/C/D assignments. You may consider sorting by "In Compliance" to locate all courses that have been reported as "No." 

Some of these courses will not be "In Compliance" because they are simply too large. This program defines a course as "In Compliance" if it has no more than 9 students to the A-group, 9 students to the B-group, 9 students to the C-group, and 9 students to the D-group. This is impossible if the course has 40 students in it. 

Other courses will not be "In Compliance" because they have an imbalance in the size of the A/B/C/D groups that is too large. You can identify these courses by looking for a large value of "Max Deviation" (as well as "In Compliance" = "No"). Sometimes, it will be possible to get some of these course to be "In Compliance" by running the algorithm longer (or running on a few machines and selecting the best results). However, schedule optimization is well known to be a difficult problem, and it is not realistic to expect 100% of courses achieving a rating of "In Compliance." 

_Note:_ This output report is still under development, particularly how to classify a course as "In Compliance." 

## Author

* **Christopher Grattoni** - *Initial work* - [ChrisGrattoni](https://github.com/ChrisGrattoni/partitionoptimizer)

See also the list of [contributors](https://github.com/ChrisGrattoni/partitionoptimizer/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks, brother.

