# Student Partition Optimization Tool for Schools (SPOTS)
State governments and public health agencies have begun recommending that schools implement "Physically Distanced Learning," with a student/teacher ratio of 10/1 or fewer in each classroom. At most schools, this will require rotating groups of students into the school building while other students stay home and learn remotely. This project aims to help schools assign students to an A/B/C/D group in a manner that allows physical distancing in as many classrooms as possible. 

Video introduction: https://youtu.be/XJFvY4-FCSc

## Getting Started

This program uses a genetic algorithm to optimize a partition of students. In order to evaluate the fitness of a given partition, the algorithm must check the partition against your school's master schedule. You will need to generate a .csv file with the following fields:
     
        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
		
The three most important columns in this .csv file are STUDENT_ID, ROOM_NUMBER, and PERIOD. The algorithm uniquely identifies individual students using STUDENT_ID, and courses within a school building are uniquely identified using the pair (ROOM_NUMBER, PERIOD).

This .csv file should have an entry for each student course enrollment. For example, if John Smith is taking 7 classes, then John Smith should have 7 rows in the .csv file:

        LAST, FIRST, MIDDLE, STUDENT_ID, COURSE_NUMBER, COURSE_NAME, COURSE_ID, ROOM_NUMBER, PERIOD
        John, Smith, William, 000281871, Math435-01,    ALGEBRA 2/TRIG,2381878, ROOM 255,    PERIOD 1
        John, Smith, William, 000281871, Eng402-01,     ADV BRITISH LIT,342243, ROOM 211,    PERIOD 2
        John, Smith, William, 000281871, Hist424-01,    AP WORLD HIST,50122439, ROOM 166,    PERIOD 3
        John, Smith, William, 000281871, Chem419-01,    AP CHEMISTRY,544433238, ROOM 200,    PERIOD 5
        John, Smith, William, 000281871, Band300-01,    MARCHING BAND,40391878, ROOM 003,    PERIOD 6
        John, Smith, William, 000281871, Germ461-01,    AP GERMAN LANG,1943981, ROOM 214,    PERIOD 7
        John, Smith, William, 000281871, Gym400-01,     ADVENTURE EDUCATION,23, ROOM GYM,    PERIOD 8


        The .csv file should have an entry for each student course enrollment.
        For example, if John Smith is taking 7 classes, then John Smith should
        have 7 rows in the .csv file:
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

