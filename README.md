## New Since the First Version

**Windows Executable:** Instead of downloading Python 3.7+, you may launch this program from *SPOTS.exe* if you are using Windows.

**Graphical Interface:** Instead of working in a command terminal, you can use an optional graphical interface.

**Sibling support:** Assign siblings (or any specified student subgroups) to the same cohort.

**Multiprocessing:** This version uses a parallel genetic algorithm to obtain significantly better results.

# Student Partition Optimization Tool for Schools (SPOTS)
State governments and public health agencies have begun recommending that schools implement "Physically Distanced Learning," with a reduced student/teacher in each classroom. At most schools, this will require rotating cohorts of students into the school building while other students stay home and learn remotely. This project aims to help schools assign students to smaller cohorts in a manner that allows physical distancing in as many classrooms as possible. 

Video introduction: https://youtu.be/XJFvY4-FCSc

### What Does This Program Do?

The Student Partition Optimization Tool for Schools uses a parallel genetic algorithm to assign each student at your school to a subgroup in a way that facilitates physical distancing in as many classrooms as possible. This program supports partitioning students into 2 cohorts (an A/B partition) or 4 cohorts (an A/B/C/D partition). For an A/B/C/D partition, a course at your school will be classified as "In Compliance" if it meets the following criteria:

1. No more than 9 students in any one cohort, more explicitly:
   - No more than 9 A's
   - No more than 9 B's
   - No more than 9 C's
   - No more than 9 D's
2. No more than 15 students when combining the A- and B-cohorts
3. No more than 15 students when combining the C- and D-cohorts

This allows schools some flexibility if they have to rotate students in and out of the building. If a school can have no more than 10 people in a classroom (9 students and 1 teacher), then the school can rotate through the A/B/C/D cohorts one at a time. If a school needs to run each classroom at approximately 50% capacity, they can bring in the A- and B-cohorts together, and then bring in the C- and D-cohorts together. 

For courses that are not initially "In Compliance," the algorithm attempts to balance the distribution of students in the A/B/C/D cohorts, as well as the distribution of students in the (A+B) and (C+D) cohorts. 

If a school has a different set of requirements than a maximum of 9 students in A/B/C/D cohorts and 15 students in (A+B) and (C+D) cohorts, then the fitness function in SPOTS.py can easily be modified to accommodate this. 

**Important:** A genetic algorithm is an optimization technique whose results improve with additional computation. You may want to let this program work for 8 hours or more to obtain desirable results.

## Prerequisites

Python 3.7+ (https://www.python.org/downloads/)

### Getting Started (Example Data)

To try this program with the provided example data, all you need to do is make sure that *SPOTS.py*, *example_student_data.csv*, and *settings.yaml* are in the same folder together. You can launch this program from the command line:

![Image of Command Line SPOTS.py Launch](https://www.compsciprinciples.com/notebooks/spots_example1.PNG)

Or if you prefer, you can launch the program from SPOTS.exe:

![Image of GUI SPOTS.exe Launch](https://www.compsciprinciples.com/notebooks/spots_example2.PNG)

When the program terminates, the parent directory of *SPOTS.py* will contain two final reports (*student_assignments.csv* and *course_analysis.csv*).

After you have the program working with example data, you can try data from your own school. 

### Getting Started (Your School's Data)

This program uses a parallel genetic algorithm to optimize a partition of students. In order to evaluate the fitness of a given partition, the algorithm must check the partition against your school's master schedule. You will need to generate a *.csv* file with the following fields:
     
        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
		
The three most important columns in this *.csv* file are STUDENT_ID, ROOM_NUMBER, and PERIOD: these cannot be omitted. The algorithm uniquely identifies individual students using STUDENT_ID. Courses within a school building are uniquely identified using the pair (ROOM_NUMBER, PERIOD). All other columns can be modified or removed (and new columns can be added) with proper modifications to the program.

This *.csv* file should have an entry for each student course enrollment. For example, if John Smith is taking 7 classes, then John Smith should have 7 rows in the *.csv* file:

        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
        John, Smith, William, 000281871, Math435-01,    ALGEBRA 2/TRIG,2381878, ROOM 255,    PERIOD 1
        John, Smith, William, 000281871, Eng402-01,     ADV BRITISH LIT,342243, ROOM 211,    PERIOD 2
        John, Smith, William, 000281871, Hist424-01,    AP WORLD HIST,50122439, ROOM 166,    PERIOD 3
        John, Smith, William, 000281871, Chem419-01,    AP CHEMISTRY,544433238, ROOM 200,    PERIOD 5
        John, Smith, William, 000281871, Band300-01,    MARCHING BAND,40391878, ROOM 003,    PERIOD 6
        John, Smith, William, 000281871, Germ461-01,    AP GERMAN LANG,1943981, ROOM 214,    PERIOD 7
        John, Smith, William, 000281871, Gym400-01,     ADVENTURE EDUCATION,23, ROOM GYM,    PERIOD 8

Once you have generated this *.csv* file, you will have to edit SPOTS.py to indicate the name of your *.csv* file so that it does not point at the example data anymore. Replace "example_student_data.csv" with the name of your specific file in *settings.yaml*:

		# Filename of .csv file with student schedule data (default = 'example_student_data.csv') 
		# Note: does not need to be an absolute path as long as the .csv and .py are in the same folder
		input_csv_filename : "example_student_data.csv" 
		
Next, if your school is implementing an A/B partition (2 cohorts of students), set number_of_partitions : 2. For an A/B/C/D partition (4 cohorts of students), leave the default value of number_of_partitions : 4. You will have to add to this project for a partition size other than 2 or 4:

		# Number of groups to partition students into (only 2 and 4 are implemented) 
		number_of_partitions : 4

You can also modify the desired size of the letter partition in each classroom. By default, the program will try to assign no more than 9 students of each letter (A/B/C/D) and 15 students in the paired cohorts ((A + B) and (C + D)). Here is where to make these changes:

		# Max size of a partition when dividing students into two cohorts (default = 15) 
		half_class_maximum : 15

		# Max size of a partition when dividing students into four cohorts (default = 9) 
		quarter_class_maximum : 9

After making these changes, you are ready to try the program out on real data. If you launch from the command line, the default setting for using the graphical interface in *settings.yaml* is set to False:

	# toggle the GUI on/off using True or False 
	# (default = False) 
	use_gui : False
	
You can change this to *True* if you prefer using a graphical interface. You can also launch the program using *SPOTS.exe*.
		
## Student Subgroup Support

There are many reasons why schools may want the ability to guarantee that a certain students receive the same letter assignment as other students. The most common case is likely to be to assign siblings to the same letter group. As a result, this program now supports "student subgroups." There are two types of subgroups that this program supports:

*Required* subgroups: The program will enforce that these subgroups be preserved. That is, if Student1 and Student2 are in a subgroup, they _must_ be assigned to the same subgroup. 

*Preferred* subgroups: The program will show a preference for preserving these subgroups, but it will prioritize physical distancing requirements over subgroup integrity. 

### Required Student Subgrouping Example

All you need to try out Student Subgroups is a *.csv* file with two columns of Student ID numbers:

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

After you try this out with example data, you can try your own *.csv* with required student pairings. 

*Warning:* Schools should be wary about assigning too many students to subgroups. This program is more effective when the algorithm can adequately explore its potential solution space. Every time a student is placed into a subgroup, this is placing a limit on the quality of the results the algorithm can produce. In my initial testing, it seems like good results can still be produced when grouping together siblings, but I have not tested what happens with much larger subgrouping restrictions.  

### Advanced Users

If you are familiar with parallel genetic algorithms (or would just like to experiment), you can try changing the default values for mutation_rate, population_size, number_of_eras, and number_of_generations_per_era. It may be possible to modify these (and other) parameters to obtain better results. Please email studentpartitionoptimizer@gmail.com if you have parameters you would like to suggest for new default values. 

Finally, a genetic algorithm is only as good as its fitness function. If you really want to experiment, find the method Schedule.fitness_score() and modify the logic. These changes can either be tailored to your school's needs, or you might make a modification to obtain optimal results in less time. Please email studentpartitionoptimizer@gmail.com if you have a suggested change to Schedule.fitness_score(). 

### Final Output 

As the algorithm runs, it will append results to the file progress_log.txt. You can check this file to watch the progress of the algorithm. Because the first generation in this algorithm assigns students to A/B/C/D cohorts randomly, early generations will have a low fitness score and a limited number of courses that are rated as "In Compliance." These early generations are similar to the quality of partitions that a human could generate by hand. You should notice a significant jump in the number of "In Compliance" courses for later generations.   

This program will also generate two final reports at the end of the algorithm: *student_assignments.csv* and *course_analysis.csv*. The student_assignments report is self-explanatory:

		Student ID, Last, First, Middle, Letter
		0291817791, Abel, Niels, Henrik, D
		0999023822, John, Mikey, Norman, A

It is just a list of students and the A/B/C/D cohorts to which they have been assigned. The course_analysis report is meant to analyze the final results of these particular A/B/C/D assignments. You may consider sorting by "In Compliance" to locate all courses that have been reported as "No." 

Some of these courses will not be "In Compliance" because they are simply too large. This program defines a course as "In Compliance" if it has no more than 9 students to the A-group, 9 students to the B-group, 9 students to the C-group, and 9 students to the D-group. This is impossible if the course has 40 students in it. 

Other courses will not be "In Compliance" because they have an imbalance in the size of the A/B/C/D cohorts that is too large. You can identify these courses by looking for a large value of "Max Deviation" (as well as "In Compliance" = "No"). Sometimes, it will be possible to get some of these course to be "In Compliance" by running the algorithm longer (or running on a few machines and selecting the best results). However, schedule optimization is well known to be a difficult problem, and it is not realistic to expect 100% of courses achieving a rating of "In Compliance." 

_Note:_ This output report is still under development, particularly how to classify a course as "In Compliance." 

## Coauthors

* **Christopher Grattoni** - *Initial work* - [ChrisGrattoni](https://github.com/ChrisGrattoni/partitionoptimizer)
* **Alice Chen** - *Visualizations & GUI* - [ayjchen1](https://github.com/ayjchen1)
* **Jerry Moon** - *Multiprocessing* - [jmoon81](https://github.com/jmoon81)
* **Eileen Peng** - *Visualizations & GUI* - [e-peng](https://github.com/e-peng)

See also the list of [contributors](https://github.com/ChrisGrattoni/partitionoptimizer/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you Alice, Eileen, Jerry and Ryan for your contributions. 
