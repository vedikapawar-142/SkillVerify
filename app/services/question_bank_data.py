"""Comprehensive 80-Question MCQ Question Bank for AI Skill Verification Platform.
Contains exactly 20 technically accurate, calibrated MCQs for each of the 4 supported languages:
1. Python (20 MCQs)
2. Java (20 MCQs)
3. C (20 MCQs)
4. C++ (20 MCQs)
Total = 80 MCQs.
"""
import json

QUESTION_BANK_DATA = [
    # =========================================================================
    # PYTHON QUESTION BANK (20 MCQs)
    # Topics: Data types, operators, conditions, loops, functions, lists,
    #         dictionaries, exceptions, debugging, scope, comprehension
    # =========================================================================
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Operators & Identity",
        "difficulty": 1,
        "statement": "In Python, what is the fundamental difference between the '==' operator and the 'is' operator?",
        "options": json.dumps([
            "A. '==' compares values for equality, whereas 'is' checks if two variables point to the same object in memory.",
            "B. '==' checks memory addresses, whereas 'is' compares data values.",
            "C. '==' is only used for numerical values, whereas 'is' is used for strings and collections.",
            "D. '==' and 'is' are completely interchangeable in Python 3."
        ]),
        "correct_answer": "A. '==' compares values for equality, whereas 'is' checks if two variables point to the same object in memory.",
        "explanation": "'==' evaluates value equality between operands, while 'is' evaluates reference identity (id(a) == id(b)).",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Data Types & Mutability",
        "difficulty": 1,
        "statement": "Which of the following built-in collection types in Python is immutable?",
        "options": json.dumps([
            "A. List",
            "B. Dictionary",
            "C. Tuple",
            "D. Set"
        ]),
        "correct_answer": "C. Tuple",
        "explanation": "Tuples in Python are immutable sequences; once created, their elements cannot be added, removed, or reassigned.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Lists & Slicing",
        "difficulty": 1,
        "statement": "What will be the output of executing `nums = [10, 20, 30, 40, 50]; print(nums[1:4])`?",
        "options": json.dumps([
            "A. [10, 20, 30]",
            "B. [20, 30, 40]",
            "C. [20, 30, 40, 50]",
            "D. [10, 20, 30, 40]"
        ]),
        "correct_answer": "B. [20, 30, 40]",
        "explanation": "List slicing `[start:stop]` includes the element at index start (1 -> 20) and excludes the element at index stop (4 -> 50).",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Loops & Control Flow",
        "difficulty": 2,
        "statement": "In Python, when does the `else` block attached to a `for` loop execute?",
        "options": json.dumps([
            "A. Only if the loop was terminated prematurely by a `break` statement.",
            "B. When the loop iterates over all items without encountering a `break` statement.",
            "C. At every iteration of the loop regardless of whether `break` is executed.",
            "D. Only when an uncaught exception occurs within the loop."
        ]),
        "correct_answer": "B. When the loop iterates over all items without encountering a `break` statement.",
        "explanation": "A loop's `else` clause runs when the loop finishes iterating naturally without hitting a `break` statement.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Functions & Default Arguments",
        "difficulty": 2,
        "statement": "What will the following code output?\n\ndef append_item(val, items=[]):\n    items.append(val)\n    return items\n\nprint(append_item(1))\nprint(append_item(2))",
        "options": json.dumps([
            "A. [1] followed by [2]",
            "B. [1] followed by [1, 2]",
            "C. [1, 2] followed by [1, 2]",
            "D. Raises a TypeError on the second call"
        ]),
        "correct_answer": "B. [1] followed by [1, 2]",
        "explanation": "Default parameter expressions in Python are evaluated once at function definition time, so mutable default arguments persist between calls.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Dictionaries & Lookup",
        "difficulty": 1,
        "statement": "What is the primary benefit of using `dict.get(key, default)` over direct subscript indexing `dict[key]`?",
        "options": json.dumps([
            "A. `dict.get()` is executed in O(log n) time instead of O(1) time.",
            "B. `dict.get()` returns the specified default value instead of raising a `KeyError` if the key is missing.",
            "C. `dict.get()` automatically inserts the key into the dictionary if absent.",
            "D. `dict.get()` allows keys that are not hashable, such as lists."
        ]),
        "correct_answer": "B. `dict.get()` returns the specified default value instead of raising a `KeyError` if the key is missing.",
        "explanation": "`dict.get(key, default)` safely returns default (or None) without throwing a KeyError when the key does not exist.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "List Comprehensions",
        "difficulty": 2,
        "statement": "What is the evaluated output of `[x * 2 for x in range(6) if x % 2 == 1]`?",
        "options": json.dumps([
            "A. [0, 4, 8]",
            "B. [2, 6, 10]",
            "C. [1, 3, 5]",
            "D. [2, 4, 6, 8, 10]"
        ]),
        "correct_answer": "B. [2, 6, 10]",
        "explanation": "The comprehension filters odd numbers in range 0..5 (which are 1, 3, 5) and multiplies each by 2 to yield [2, 6, 10].",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Exceptions & Handling",
        "difficulty": 2,
        "statement": "What is the guaranteed execution order of clauses in a full `try-except-else-finally` block when no exception is raised?",
        "options": json.dumps([
            "A. `try` -> `finally` -> `else`",
            "B. `try` -> `else` -> `finally`",
            "C. `try` -> `except` -> `finally`",
            "D. `try` -> `finally`"
        ]),
        "correct_answer": "B. `try` -> `else` -> `finally`",
        "explanation": "When no exception occurs, Python executes the `try` block, followed by the `else` block, and always finishes with the `finally` block.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Functions & Unpacking",
        "difficulty": 2,
        "statement": "In a Python function definition `def process(*args, **kwargs):`, what types are `args` and `kwargs` inside the function body?",
        "options": json.dumps([
            "A. `args` is a list and `kwargs` is a list of tuples.",
            "B. `args` is a tuple and `kwargs` is a dictionary.",
            "C. Both `args` and `kwargs` are dictionaries.",
            "D. Both `args` and `kwargs` are tuples."
        ]),
        "correct_answer": "B. `args` is a tuple and `kwargs` is a dictionary.",
        "explanation": "`*args` collects positional arguments into a tuple, while `**kwargs` collects keyword arguments into a standard Python dict.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Variable Scope & LEGB",
        "difficulty": 2,
        "statement": "Which keyword must be used inside a nested function to modify a variable defined in the immediately enclosing non-global scope?",
        "options": json.dumps([
            "A. `global`",
            "B. `nonlocal`",
            "C. `outer`",
            "D. `super`"
        ]),
        "correct_answer": "B. `nonlocal`",
        "explanation": "The `nonlocal` keyword allows reassigning variables in the nearest enclosing non-global scope.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "String Operations",
        "difficulty": 1,
        "statement": "What will be the output of `'-'.join(['AI', 'Skill', 'Platform'])`?",
        "options": json.dumps([
            "A. 'AI-Skill-Platform-'",
            "B. 'AI-Skill-Platform'",
            "C. ['AI-', 'Skill-', 'Platform']",
            "D. '-AI-Skill-Platform'"
        ]),
        "correct_answer": "B. 'AI-Skill-Platform'",
        "explanation": "`str.join(iterable)` inserts the delimiter string strictly between the elements of the iterable.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Context Managers",
        "difficulty": 2,
        "statement": "What is the primary technical advantage of managing file I/O with the `with open(...) as f:` statement?",
        "options": json.dumps([
            "A. It reads file contents faster by skipping disk buffering.",
            "B. It guarantees the file stream is closed upon block exit, even if an uncaught exception is thrown.",
            "C. It automatically parses file content into a JSON object.",
            "D. It prevents multiple threads from opening other files."
        ]),
        "correct_answer": "B. It guarantees the file stream is closed upon block exit, even if an uncaught exception is thrown.",
        "explanation": "The context manager protocol calls `__exit__()` on the file object, ensuring reliable cleanup and resource release.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Generators & Yield",
        "difficulty": 3,
        "statement": "What happens when a Python function containing a `yield` statement is initially invoked?",
        "options": json.dumps([
            "A. It executes the entire function body and returns a list of values.",
            "B. It returns a generator iterator object without executing the function body until `next()` or iteration begins.",
            "C. It immediately raises a StopIteration exception.",
            "D. It spawns a concurrent OS thread to compute items in the background."
        ]),
        "correct_answer": "B. It returns a generator iterator object without executing the function body until `next()` or iteration begins.",
        "explanation": "Calling a generator function produces a generator object; execution pauses at the beginning until `next()` is called.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Lambda & Built-ins",
        "difficulty": 1,
        "statement": "What is the output of `list(map(lambda x: x ** 2, [1, 2, 3, 4]))`?",
        "options": json.dumps([
            "A. [1, 4, 9, 16]",
            "B. [2, 4, 6, 8]",
            "C. [1, 2, 3, 4]",
            "D. 30"
        ]),
        "correct_answer": "A. [1, 4, 9, 16]",
        "explanation": "`map()` applies the lambda function `x ** 2` to each integer element in the input list.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Object-Oriented Programming",
        "difficulty": 2,
        "statement": "In Python class design, what is the key difference between `__str__` and `__repr__` methods?",
        "options": json.dumps([
            "A. `__str__` is intended to be human-readable, while `__repr__` is intended to be unambiguous and helpful for developers/debugging.",
            "B. `__str__` is called by `eval()`, whereas `__repr__` is called by `print()`.",
            "C. `__str__` returns bytes, whereas `__repr__` returns Unicode text.",
            "D. `__str__` is mandatory in every class, while `__repr__` is deprecated."
        ]),
        "correct_answer": "A. `__str__` is intended to be human-readable, while `__repr__` is intended to be unambiguous and helpful for developers/debugging.",
        "explanation": "`__str__` aims for an informal, readable string representation, whereas `__repr__` aims to be formal, unambiguous, and ideally valid code.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Class vs Static Methods",
        "difficulty": 2,
        "statement": "Which decorator is used to define a method that receives the class itself (`cls`) as its implicit first argument rather than an instance?",
        "options": json.dumps([
            "A. `@staticmethod`",
            "B. `@classmethod`",
            "C. `@property`",
            "D. `@abstractmethod`"
        ]),
        "correct_answer": "B. `@classmethod`",
        "explanation": "`@classmethod` passes the calling class object as the first parameter conventionally named `cls`.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Sets & Uniqueness",
        "difficulty": 1,
        "statement": "What will be the result of `len(set([1, 2, 2, 3, 4, 4, 4]))`?",
        "options": json.dumps([
            "A. 7",
            "B. 4",
            "C. 3",
            "D. 1"
        ]),
        "correct_answer": "B. 4",
        "explanation": "A set only stores unique elements; duplicates {2, 4} are discarded, leaving {1, 2, 3, 4} with length 4.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Debugging & Exceptions",
        "difficulty": 1,
        "statement": "Which exception is raised when attempting to access a list index that is greater than or equal to the length of the list?",
        "options": json.dumps([
            "A. `KeyError`",
            "B. `IndexError`",
            "C. `ValueError`",
            "D. `AttributeError`"
        ]),
        "correct_answer": "B. `IndexError`",
        "explanation": "Accessing an out-of-range integer index in a sequence raises `IndexError: list index out of range`.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Copies: Shallow vs Deep",
        "difficulty": 3,
        "statement": "What happens when you create a shallow copy of a nested list `b = copy.copy(a)` in Python?",
        "options": json.dumps([
            "A. Both the outer list and all inner nested objects are completely duplicated in new memory addresses.",
            "B. A new outer list is created, but references to inner nested objects are shared between `a` and `b`.",
            "C. `b` is merely an alias pointing to the identical memory address as `a`.",
            "D. Inner nested lists are converted into immutable tuples."
        ]),
        "correct_answer": "B. A new outer list is created, but references to inner nested objects are shared between `a` and `b`.",
        "explanation": "Shallow copy constructs a new collection object and then inserts references into it to the objects found in the original.",
        "marks": 100
    },
    {
        "skill": "python",
        "type": "mcq",
        "topic": "Collections & Counting",
        "difficulty": 2,
        "statement": "In the standard library module `collections`, what data structure provides an efficient multiset counter for hashable objects?",
        "options": json.dumps([
            "A. `collections.defaultdict`",
            "B. `collections.Counter`",
            "C. `collections.deque`",
            "D. `collections.OrderedDict`"
        ]),
        "correct_answer": "B. `collections.Counter`",
        "explanation": "`Counter` is a `dict` subclass designed for counting hashable objects with convenient methods like `most_common()`.",
        "marks": 100
    },

    # =========================================================================
    # JAVA QUESTION BANK (20 MCQs)
    # Topics: Data types, Strings, OOP, Inheritance, Interfaces, Access modifiers,
    #         Exceptions, Collections, Polymorphism, Static & Final, Memory
    # =========================================================================
    {
        "skill": "java",
        "type": "mcq",
        "topic": "String Immutability & Pool",
        "difficulty": 1,
        "statement": "What will the following Java code snippet print?\n\nString s1 = \"hello\";\nString s2 = new String(\"hello\");\nSystem.out.println(s1 == s2);\nSystem.out.println(s1.equals(s2));",
        "options": json.dumps([
            "A. true followed by true",
            "B. false followed by true",
            "C. true followed by false",
            "D. false followed by false"
        ]),
        "correct_answer": "B. false followed by true",
        "explanation": "`==` checks reference equality (s2 is explicitly allocated on the heap, s1 in string constant pool), whereas `.equals()` checks character sequence value equality.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Primitive Types & Autoboxing",
        "difficulty": 1,
        "statement": "Which of the following represents the correct wrapper class for the primitive type `int` in Java?",
        "options": json.dumps([
            "A. Int",
            "B. Integer",
            "C. Number",
            "D. IntWrapper"
        ]),
        "correct_answer": "B. Integer",
        "explanation": "In Java's `java.lang` package, the object wrapper for the primitive `int` is `java.lang.Integer`.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Access Modifiers",
        "difficulty": 2,
        "statement": "Which access modifier in Java restricts member visibility strictly to the declaring class, its subclasses in any package, and all other classes in the same package?",
        "options": json.dumps([
            "A. private",
            "B. default (package-private)",
            "C. protected",
            "D. public"
        ]),
        "correct_answer": "C. protected",
        "explanation": "Members marked `protected` are accessible within the same package and by subclasses located in other packages.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "The final Keyword",
        "difficulty": 2,
        "statement": "What happens if a Java class is declared with the `final` keyword?",
        "options": json.dumps([
            "A. No instances of the class can ever be created.",
            "B. The class cannot be extended (subclassed) by any other class.",
            "C. All methods inside the class must be declared static.",
            "D. All variables inside the class must be initialized to null."
        ]),
        "correct_answer": "B. The class cannot be extended (subclassed) by any other class.",
        "explanation": "A `final` class prevents inheritance; for example, `java.lang.String` and `java.lang.Math` are final classes.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Inheritance & Super",
        "difficulty": 2,
        "statement": "In a subclass constructor, what statement must be the very first line of code if calling a parent constructor?",
        "options": json.dumps([
            "A. `this();`",
            "B. `super();`",
            "C. `parent();`",
            "D. `base();`"
        ]),
        "correct_answer": "B. `super();`",
        "explanation": "A call to `super()` or `this()` must be the first statement in a constructor to ensure parent initialization completes first.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Method Overloading vs Overriding",
        "difficulty": 2,
        "statement": "Which of the following rules is mandatory for valid method overriding in Java?",
        "options": json.dumps([
            "A. The overriding method in the subclass must have a different parameter list.",
            "B. The overriding method must have the exact same method signature and a compatible return type.",
            "C. The overriding method must declare a more restrictive access modifier than the superclass method.",
            "D. Overridden methods can only be defined inside abstract classes."
        ]),
        "correct_answer": "B. The overriding method must have the exact same method signature and a compatible return type.",
        "explanation": "Overriding requires the same name, exact same parameter types/order, and a covariant (compatible) return type, without reducing visibility.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Interfaces & Default Methods",
        "difficulty": 2,
        "statement": "Since Java 8, which keyword permits interfaces to provide a concrete method implementation with a default body?",
        "options": json.dumps([
            "A. `static` only",
            "B. `default`",
            "C. `concrete`",
            "D. `virtual`"
        ]),
        "correct_answer": "B. `default`",
        "explanation": "Java 8 introduced `default` methods in interfaces to enable backwards-compatible library enhancements.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Exception Handling",
        "difficulty": 2,
        "statement": "Which of the following exceptions in Java is an UNCHECKED (runtime) exception?",
        "options": json.dumps([
            "A. `java.io.IOException`",
            "B. `java.sql.SQLException`",
            "C. `java.lang.NullPointerException`",
            "D. `java.lang.ClassNotFoundException`"
        ]),
        "correct_answer": "C. `java.lang.NullPointerException`",
        "explanation": "Subclasses of `RuntimeException` (such as `NullPointerException`, `IndexOutOfBoundsException`) are unchecked exceptions.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Collections: List Types",
        "difficulty": 2,
        "statement": "In terms of computational complexity, what is the time complexity for getting an element by index in `ArrayList` vs `LinkedList`?",
        "options": json.dumps([
            "A. O(1) in ArrayList, O(n) in LinkedList",
            "B. O(n) in ArrayList, O(1) in LinkedList",
            "C. O(1) in both ArrayList and LinkedList",
            "D. O(log n) in ArrayList, O(1) in LinkedList"
        ]),
        "correct_answer": "A. O(1) in ArrayList, O(n) in LinkedList",
        "explanation": "`ArrayList` uses a contiguous dynamic array providing O(1) random access, whereas `LinkedList` must traverse nodes in O(n) time.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Collections: Map Contract",
        "difficulty": 3,
        "statement": "When creating a custom class to use as a key in a `java.util.HashMap`, which two methods MUST be consistently overridden?",
        "options": json.dumps([
            "A. `compareTo()` and `toString()`",
            "B. `hashCode()` and `equals()`",
            "C. `clone()` and `hashCode()`",
            "D. `finalize()` and `equals()`"
        ]),
        "correct_answer": "B. `hashCode()` and `equals()`",
        "explanation": "If two objects are equal according to `equals(Object)`, they must produce identical `hashCode()` results for hash bucket resolution.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "StringBuilder vs String",
        "difficulty": 1,
        "statement": "Why is `StringBuilder` preferred over regular `String` concatenation inside large loops in Java?",
        "options": json.dumps([
            "A. `StringBuilder` is synchronized and thread-safe.",
            "B. `StringBuilder` mutates a single internal buffer instead of allocating new intermediate String objects on the heap.",
            "C. `StringBuilder` writes directly to disk storage.",
            "D. `StringBuilder` uses static memory instead of heap memory."
        ]),
        "correct_answer": "B. `StringBuilder` mutates a single internal buffer instead of allocating new intermediate String objects on the heap.",
        "explanation": "`StringBuilder` is mutable and appends characters in-place, avoiding the quadratic memory churn of repeated immutable String allocations.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "The static Keyword",
        "difficulty": 1,
        "statement": "What will happen if you attempt to access an instance variable from inside a `static` method without creating an object?",
        "options": json.dumps([
            "A. The code compiles and reads the default null or 0 value.",
            "B. A compile-time error occurs: non-static variable cannot be referenced from a static context.",
            "C. A NullPointerException is thrown at runtime.",
            "D. The instance variable is automatically converted into a static variable."
        ]),
        "correct_answer": "B. A compile-time error occurs: non-static variable cannot be referenced from a static context.",
        "explanation": "Static methods belong to the class definition and have no implicit `this` reference to inspect instance-level state.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Polymorphism & Binding",
        "difficulty": 2,
        "statement": "What kind of polymorphism does method overriding in Java represent?",
        "options": json.dumps([
            "A. Compile-time (static) polymorphism",
            "B. Runtime (dynamic method dispatch) polymorphism",
            "C. Preprocessor macro polymorphism",
            "D. Generic type erasure polymorphism"
        ]),
        "correct_answer": "B. Runtime (dynamic method dispatch) polymorphism",
        "explanation": "Method overriding is resolved dynamically at runtime based on the actual object instance type (dynamic binding).",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Control Structures: Switch",
        "difficulty": 1,
        "statement": "What occurs in a standard Java `switch` block if a `case` matches but does NOT contain a `break` statement?",
        "options": json.dumps([
            "A. The switch block throws a BreakNotFoundException.",
            "B. Execution 'falls through' to the subsequent case statements regardless of their conditions.",
            "C. The switch automatically terminates at the end of the matched case.",
            "D. The compiler rejects the program with a syntax error."
        ]),
        "correct_answer": "B. Execution 'falls through' to the subsequent case statements regardless of their conditions.",
        "explanation": "Without `break`, Java exhibits fall-through behavior, executing code in subsequent cases until a break or switch end is reached.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Memory Architecture",
        "difficulty": 2,
        "statement": "In Java's memory model, where are local primitive variables and method call frames stored?",
        "options": json.dumps([
            "A. Heap memory",
            "B. Stack memory",
            "C. Metaspace",
            "D. Native OS disk cache"
        ]),
        "correct_answer": "B. Stack memory",
        "explanation": "Thread call stacks hold active stack frames containing local primitive variables and object reference pointers.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Arrays in Java",
        "difficulty": 1,
        "statement": "What is the proper syntax to determine the number of elements in an array `int[] arr = new int[10];` in Java?",
        "options": json.dumps([
            "A. `arr.length()`",
            "B. `arr.size()`",
            "C. `arr.length`",
            "D. `arr.count()`"
        ]),
        "correct_answer": "C. `arr.length`",
        "explanation": "In Java, an array has a built-in public final field named `length` (unlike Collections which use the method `.size()`).",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Abstract Classes vs Interfaces",
        "difficulty": 2,
        "statement": "Which statement correctly describes a capability of abstract classes that interfaces do NOT possess in Java?",
        "options": json.dumps([
            "A. Abstract classes can define method signatures.",
            "B. Abstract classes can declare constructors and maintain mutable instance fields with state.",
            "C. Abstract classes can be instantiated directly with `new`.",
            "D. Multiple abstract classes can be inherited by a single subclass simultaneously."
        ]),
        "correct_answer": "B. Abstract classes can declare constructors and maintain mutable instance fields with state.",
        "explanation": "Abstract classes have constructors (invoked by `super()`) and can hold instance state, whereas interface fields are implicitly `public static final`.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Exception Handling: Finally",
        "difficulty": 2,
        "statement": "Under what circumstance will a `finally` block in Java NOT execute after a `try` block?",
        "options": json.dumps([
            "A. If a `return` statement is executed inside the `try` block.",
            "B. If `System.exit(0)` is invoked inside the `try` block.",
            "C. If an unhandled NullPointerException is thrown.",
            "D. If the `try` block contains an inner loop."
        ]),
        "correct_answer": "B. If `System.exit(0)` is invoked inside the `try` block.",
        "explanation": "`System.exit()` terminates the Java Virtual Machine immediately, preventing execution of any pending `finally` blocks.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Generics & Type Safety",
        "difficulty": 2,
        "statement": "What is the primary compilation process in Java that enforces compile-time type safety while ensuring backward compatibility with older bytecodes?",
        "options": json.dumps([
            "A. Dynamic dispatch",
            "B. Type erasure",
            "C. Just-In-Time compilation",
            "D. Reflection injection"
        ]),
        "correct_answer": "B. Type erasure",
        "explanation": "Java compiler uses type erasure: generic type parameters are verified at compile time and removed/replaced with Object in bytecodes.",
        "marks": 100
    },
    {
        "skill": "java",
        "type": "mcq",
        "topic": "Pass-by-Value Semantics",
        "difficulty": 3,
        "statement": "How does Java handle argument passing to methods for object references?",
        "options": json.dumps([
            "A. Pass-by-reference: the method can rebind the caller's reference variable to a new object.",
            "B. Pass-by-value: the method receives a copy of the reference address, so modifying the object mutates it, but reassigning the reference does not affect the caller.",
            "C. Pass-by-name: expressions are evaluated lazily.",
            "D. Pass-by-constant: objects cannot be modified inside methods."
        ]),
        "correct_answer": "B. Pass-by-value: the method receives a copy of the reference address, so modifying the object mutates it, but reassigning the reference does not affect the caller.",
        "explanation": "Java is strictly pass-by-value. For objects, the value passed is the memory reference bits; reassignment inside the method does not alter caller's reference.",
        "marks": 100
    },

    # =========================================================================
    # C QUESTION BANK (20 MCQs)
    # Topics: Data types, Operators, Pointers, Arrays, Strings, Dynamic Memory,
    #         Storage Classes, Structs, Unions, Preprocessor, File I/O
    # =========================================================================
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Operators: Increment",
        "difficulty": 1,
        "statement": "What will be printed by the following C code snippet?\n\nint a = 5;\nint b = a++;\nint c = ++a;\nprintf(\"%d %d %d\", a, b, c);",
        "options": json.dumps([
            "A. 7 5 7",
            "B. 7 6 7",
            "C. 6 5 6",
            "D. 7 5 6"
        ]),
        "correct_answer": "A. 7 5 7",
        "explanation": "`b = a++` assigns 5 to b, then increments a to 6. `c = ++a` increments a to 7 first, then assigns 7 to c. Final values: a=7, b=5, c=7.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Data Types & Sizeof",
        "difficulty": 1,
        "statement": "What does the `sizeof` operator in C evaluate to?",
        "options": json.dumps([
            "A. The number of bits allocated to a type or expression.",
            "B. The size in bytes of the operand, represented as a `size_t` value.",
            "C. The memory address of the first byte of the variable.",
            "D. The number of elements in any dynamically allocated heap buffer."
        ]),
        "correct_answer": "B. The size in bytes of the operand, represented as a `size_t` value.",
        "explanation": "`sizeof` yields the storage size in bytes (where sizeof(char) is defined to be 1 byte).",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Pointers: Dereference",
        "difficulty": 1,
        "statement": "Given `int x = 42; int *ptr = &x;`, which expression accesses or modifies the value of `x` through the pointer?",
        "options": json.dumps([
            "A. `&ptr`",
            "B. `*ptr`",
            "C. `ptr->value`",
            "D. `ptr.x`"
        ]),
        "correct_answer": "B. `*ptr`",
        "explanation": "The unary `*` dereference operator accesses the value stored at the memory location addressed by `ptr`.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Pointer Arithmetic",
        "difficulty": 2,
        "statement": "If `ptr` is an `int*` pointing to address 0x1000 on a 32/64-bit architecture where `sizeof(int) == 4`, what address is `ptr + 2`?",
        "options": json.dumps([
            "A. 0x1002",
            "B. 0x1004",
            "C. 0x1008",
            "D. 0x1010"
        ]),
        "correct_answer": "C. 0x1008",
        "explanation": "Pointer arithmetic scales offsets by the byte size of the pointed-to type: 0x1000 + (2 * 4) = 0x1008.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Strings & Null Terminator",
        "difficulty": 1,
        "statement": "In C, how are literal strings terminated in memory?",
        "options": json.dumps([
            "A. With a newline character '\\n'",
            "B. With a null character '\\0' (ASCII 0)",
            "C. With an end-of-file indicator EOF",
            "D. With a semicolon ';'"
        ]),
        "correct_answer": "B. With a null character '\\0' (ASCII 0)",
        "explanation": "C strings are null-terminated character sequences ending with a sentinel byte `\\0`.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "String Functions",
        "difficulty": 2,
        "statement": "What will `strlen(\"Verify\")` return compared to `sizeof(\"Verify\")`?",
        "options": json.dumps([
            "A. `strlen` returns 6, `sizeof` returns 7",
            "B. Both return 6",
            "C. Both return 7",
            "D. `strlen` returns 7, `sizeof` returns 6"
        ]),
        "correct_answer": "A. `strlen` returns 6, `sizeof` returns 7",
        "explanation": "`strlen()` counts characters up to (excluding) `\\0` (6 bytes), while `sizeof` includes the terminal `\\0` character (7 bytes).",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Dynamic Memory: Malloc vs Calloc",
        "difficulty": 2,
        "statement": "What is the primary distinction between `malloc()` and `calloc()` in C?",
        "options": json.dumps([
            "A. `malloc()` allocates from stack; `calloc()` allocates from heap.",
            "B. `calloc()` allocates memory and initializes all allocated bytes to zero; `malloc()` leaves memory uninitialized (indeterminate).",
            "C. `malloc()` can allocate multi-dimensional arrays, whereas `calloc()` cannot.",
            "D. `calloc()` automatically frees memory when out of scope."
        ]),
        "correct_answer": "B. `calloc()` allocates memory and initializes all allocated bytes to zero; `malloc()` leaves memory uninitialized (indeterminate).",
        "explanation": "`calloc(num, size)` zero-initializes the allocated memory block, whereas `malloc(size)` leaves existing junk bytes untouched.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Memory Leaks & Free",
        "difficulty": 2,
        "statement": "What dangerous programming error occurs when allocated heap memory is freed, but the pointer continues to be dereferenced by subsequent code?",
        "options": json.dumps([
            "A. Stack overflow",
            "B. Dangling pointer error",
            "C. Deadlock",
            "D. Linker relocation error"
        ]),
        "correct_answer": "B. Dangling pointer error",
        "explanation": "A pointer pointing to deallocated memory is a dangling pointer; dereferencing it causes undefined behavior.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Storage Classes",
        "difficulty": 2,
        "statement": "In C, what is the effect of declaring a local variable inside a function with the `static` keyword?",
        "options": json.dumps([
            "A. The variable cannot be modified (it becomes read-only).",
            "B. The variable is allocated in the data segment and retains its value between successive calls to that function.",
            "C. The variable is accessible from all other C source files.",
            "D. The variable is stored in a CPU hardware register."
        ]),
        "correct_answer": "B. The variable is allocated in the data segment and retains its value between successive calls to that function.",
        "explanation": "Local `static` variables have static storage duration: they persist throughout the entire program execution.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Structures & Member Access",
        "difficulty": 1,
        "statement": "Given `struct Student s; struct Student *p = &s;`, which operator is used to access members through pointer `p`?",
        "options": json.dumps([
            "A. `p.name`",
            "B. `p->name`",
            "C. `p::name`",
            "D. `p#name`"
        ]),
        "correct_answer": "B. `p->name`",
        "explanation": "The arrow operator `->` is syntactic sugar for dereferencing and accessing a struct field: `(*p).name`.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Structs vs Unions",
        "difficulty": 2,
        "statement": "What is the defining structural difference between a `struct` and a `union` in C?",
        "options": json.dumps([
            "A. A `struct` cannot contain pointer members, whereas a `union` can.",
            "B. In a `struct`, every member has its own distinct memory offset; in a `union`, all members share the exact same base memory location.",
            "C. `struct` members are always private; `union` members are always public.",
            "D. A `union` has a size equal to the sum of all its member sizes."
        ]),
        "correct_answer": "B. In a `struct`, every member has its own distinct memory offset; in a `union`, all members share the exact same base memory location.",
        "explanation": "A union's size is determined by its largest member, and all members overlap at byte offset 0.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Pointers to Pointers",
        "difficulty": 3,
        "statement": "What does the declaration `int **ptr;` declare?",
        "options": json.dumps([
            "A. An array of integers of size 2.",
            "B. A pointer to a pointer to an integer.",
            "C. A pointer to a function returning an integer.",
            "D. A constant integer pointer."
        ]),
        "correct_answer": "B. A pointer to a pointer to an integer.",
        "explanation": "`int **ptr;` declares a double pointer: a variable that stores the memory address of an `int*` pointer.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Bitwise Operators",
        "difficulty": 2,
        "statement": "What is the result of the bitwise operation `(12 & 10)` in C?",
        "options": json.dumps([
            "A. 14",
            "B. 8",
            "C. 2",
            "D. 0"
        ]),
        "correct_answer": "B. 8",
        "explanation": "Binary 12 is 1100, binary 10 is 1010. Bitwise AND (1100 & 1010) = 1000 in binary, which is decimal 8.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Preprocessor Directives",
        "difficulty": 1,
        "statement": "Which preprocessor directive is used to prevent duplicate header inclusion in C source files?",
        "options": json.dumps([
            "A. `#pragma once` or `#ifndef ... #define ... #endif`",
            "B. `#include_guard`",
            "C. `#stop_duplicate`",
            "D. `#extern_include`"
        ]),
        "correct_answer": "A. `#pragma once` or `#ifndef ... #define ... #endif`",
        "explanation": "Include guards using `#ifndef ... #define ... #endif` or `#pragma once` ensure header contents are parsed once per translation unit.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "File I/O in C",
        "difficulty": 2,
        "statement": "What value does `fopen()` return if a requested file cannot be found or opened?",
        "options": json.dumps([
            "A. -1",
            "B. NULL",
            "C. 0",
            "D. EOF"
        ]),
        "correct_answer": "B. NULL",
        "explanation": "`fopen()` returns a `FILE*` stream pointer on success, or `NULL` if an error occurs opening the file.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Arrays & Pointer Decay",
        "difficulty": 2,
        "statement": "When an array name `int arr[10];` is passed into a function `void func(int arr[])`, what is actually received by the function?",
        "options": json.dumps([
            "A. A complete deep copy of the 10-element array on the stack.",
            "B. A pointer to the first element (`int *`) of the array.",
            "C. The length of the array as an integer.",
            "D. An array descriptor struct."
        ]),
        "correct_answer": "B. A pointer to the first element (`int *`) of the array.",
        "explanation": "In C, array arguments decay into a pointer to their initial element (`&arr[0]`) when passed into functions.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Format Specifiers",
        "difficulty": 1,
        "statement": "Which format specifier should be used in `printf` to print a pointer address in hexadecimal notation?",
        "options": json.dumps([
            "A. `%d`",
            "B. `%p`",
            "C. `%x`",
            "D. `%a`"
        ]),
        "correct_answer": "B. `%p`",
        "explanation": "`%p` is the standard C conversion specifier specifically defined for printing pointer memory addresses (as `void*`).",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Const Qualifiers",
        "difficulty": 3,
        "statement": "What is the difference between `const int *ptr;` and `int * const ptr;`?",
        "options": json.dumps([
            "A. `const int *ptr;` has a pointer that can change but the pointed-to int is constant; `int * const ptr;` has a constant pointer that cannot point elsewhere.",
            "B. There is no difference; both are interchangeable.",
            "C. `const int *ptr;` is stored in read-only RAM, while `int * const ptr;` is stored on the heap.",
            "D. The second declaration is invalid C syntax."
        ]),
        "correct_answer": "A. `const int *ptr;` has a pointer that can change but the pointed-to int is constant; `int * const ptr;` has a constant pointer that cannot point elsewhere.",
        "explanation": "`const int *ptr` means the value pointed to is read-only; `int * const ptr` means the pointer address itself cannot be changed.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "Recursion & Base Case",
        "difficulty": 2,
        "statement": "What critical runtime condition occurs in C when a recursive function fails to hit its base termination condition?",
        "options": json.dumps([
            "A. Heap fragmentation",
            "B. Stack overflow",
            "C. Integer overflow",
            "D. Bus error"
        ]),
        "correct_answer": "B. Stack overflow",
        "explanation": "Infinite recursion continuously pushes stack frames until the thread's call stack memory limit is exceeded, crashing with a stack overflow.",
        "marks": 100
    },
    {
        "skill": "c",
        "type": "mcq",
        "topic": "String Comparison",
        "difficulty": 1,
        "statement": "What does `strcmp(str1, str2)` return when both strings contain identical character contents?",
        "options": json.dumps([
            "A. 1",
            "B. -1",
            "C. 0",
            "D. true"
        ]),
        "correct_answer": "C. 0",
        "explanation": "`strcmp()` returns 0 when strings match, a negative value when str1 < str2, and a positive value when str1 > str2.",
        "marks": 100
    },

    # =========================================================================
    # C++ QUESTION BANK (20 MCQs)
    # Topics: References vs Pointers, OOP, Constructors/Destructors, Overloading,
    #         Inheritance, Virtual Functions & Polymorphism, STL Vector/Map,
    #         Templates, Smart Pointers, Exceptions
    # =========================================================================
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "References vs Pointers",
        "difficulty": 1,
        "statement": "In C++, what is a key distinction between a reference (`int &ref = x;`) and a pointer (`int *ptr = &x;`)?",
        "options": json.dumps([
            "A. A reference can be null and reassigned to bind to different variables at runtime.",
            "B. A reference must be initialized when declared and cannot be reseated to refer to another object.",
            "C. A reference requires the `->` operator to access struct or class members.",
            "D. References are always allocated dynamically on the heap."
        ]),
        "correct_answer": "B. A reference must be initialized when declared and cannot be reseated to refer to another object.",
        "explanation": "C++ references are aliases for existing objects; they cannot be null and cannot be rebound to refer to a different variable.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Constructors & Destructors",
        "difficulty": 1,
        "statement": "In what order are destructors called in C++ when multiple local stack objects go out of scope?",
        "options": json.dumps([
            "A. In the exact same order as they were constructed (FIFO).",
            "B. In the reverse order of their construction (LIFO).",
            "C. In alphabetical order of their variable names.",
            "D. Destructors are only called when `delete` is explicitly executed."
        ]),
        "correct_answer": "B. In the reverse order of their construction (LIFO).",
        "explanation": "Automatic stack objects are destroyed in exact reverse order of construction (Last-In, First-Out).",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Virtual Functions & Polymorphism",
        "difficulty": 2,
        "statement": "In C++, which keyword enables dynamic (runtime) dispatch for member functions through base class pointers?",
        "options": json.dumps([
            "A. `dynamic`",
            "B. `virtual`",
            "C. `override` only",
            "D. `polymorphic`"
        ]),
        "correct_answer": "B. `virtual`",
        "explanation": "Declaring a method `virtual` instructs the compiler to use a virtual method table (vtable) for dynamic dispatch at runtime.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Abstract Classes & Pure Virtual",
        "difficulty": 2,
        "statement": "How is a pure virtual function declared in a C++ class?",
        "options": json.dumps([
            "A. `virtual void func() = 0;`",
            "B. `abstract void func();`",
            "C. `virtual void func() = null;`",
            "D. `pure virtual void func();`"
        ]),
        "correct_answer": "A. `virtual void func() = 0;`",
        "explanation": "Appending `= 0` to a virtual function declaration makes it pure virtual, turning the containing class into an abstract class.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Virtual Destructors",
        "difficulty": 2,
        "statement": "Why should a base class designed for inheritance always declare its destructor as `virtual`?",
        "options": json.dumps([
            "A. To make the class an abstract base class automatically.",
            "B. To ensure the derived class destructor is invoked when deleting a derived object via a base class pointer.",
            "C. To prevent the derived class from defining its own destructor.",
            "D. To force stack-only allocation of instances."
        ]),
        "correct_answer": "B. To ensure the derived class destructor is invoked when deleting a derived object via a base class pointer.",
        "explanation": "Without a virtual base destructor, `delete basePtr` only calls the base destructor, leaking derived class resources.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "STL: Vector Operations",
        "difficulty": 1,
        "statement": "Which member function of `std::vector` appends an element to the end of the container, resizing capacity if necessary?",
        "options": json.dumps([
            "A. `append()`",
            "B. `push_back()`",
            "C. `add()`",
            "D. `insert_end()`"
        ]),
        "correct_answer": "B. `push_back()`",
        "explanation": "`std::vector::push_back()` appends an item to the end with amortized O(1) time complexity.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "STL: Map vs Unordered Map",
        "difficulty": 2,
        "statement": "What is the underlying data structure and lookup time complexity of `std::map` in standard C++?",
        "options": json.dumps([
            "A. Hash table with O(1) average lookup",
            "B. Balanced Binary Search Tree (Red-Black Tree) with O(log n) lookup",
            "C. Linked list with O(n) lookup",
            "D. Contiguous array with O(n) lookup"
        ]),
        "correct_answer": "B. Balanced Binary Search Tree (Red-Black Tree) with O(log n) lookup",
        "explanation": "`std::map` stores keys in sorted order using a self-balancing binary search tree (typically Red-Black Tree) with O(log n) search.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Templates: Generic Programming",
        "difficulty": 2,
        "statement": "What is the correct syntax for declaring a generic template function in C++?",
        "options": json.dumps([
            "A. `generic<class T> T add(T a, T b)`",
            "B. `template <typename T> T add(T a, T b)`",
            "C. `def template<T> add(T a, T b)`",
            "D. `class<T> T add(T a, T b)`"
        ]),
        "correct_answer": "B. `template <typename T> T add(T a, T b)`",
        "explanation": "Template declarations use the `template <typename T>` or `template <class T>` prefix syntax.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Operator Overloading",
        "difficulty": 2,
        "statement": "Which of the following operators CANNOT be overloaded in C++?",
        "options": json.dumps([
            "A. `+`",
            "B. `==`",
            "C. `::` (scope resolution)",
            "D. `[]` (subscript)"
        ]),
        "correct_answer": "C. `::` (scope resolution)",
        "explanation": "The operators `::` (scope resolution), `.` (member selection), and `.*` (pointer to member) cannot be overloaded in C++.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Friend Functions",
        "difficulty": 2,
        "statement": "What special privilege does declaring a function as a `friend` inside a C++ class grant it?",
        "options": json.dumps([
            "A. The function becomes an inherited virtual method in all subclasses.",
            "B. The non-member function is granted direct access to `private` and `protected` members of the class.",
            "C. The function can only be invoked by instances of that class.",
            "D. The function is executed in a privileged supervisor CPU mode."
        ]),
        "correct_answer": "B. The non-member function is granted direct access to `private` and `protected` members of the class.",
        "explanation": "A `friend` declaration allows an external function or class to access private and protected members of the granting class.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Copy Constructor",
        "difficulty": 2,
        "statement": "What is the standard parameter signature for a copy constructor in class `Widget`?",
        "options": json.dumps([
            "A. `Widget(Widget w)`",
            "B. `Widget(const Widget &other)`",
            "C. `Widget(Widget *other)`",
            "D. `Widget(const Widget other)`"
        ]),
        "correct_answer": "B. `Widget(const Widget &other)`",
        "explanation": "Copy constructors take a reference to const: `Widget(const Widget &other)`. Passing by value would trigger infinite recursion.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Modern C++: unique_ptr",
        "difficulty": 2,
        "statement": "What unique ownership semantics does `std::unique_ptr` enforce in Modern C++ (C++11 and later)?",
        "options": json.dumps([
            "A. Multiple pointers can share ownership via reference counting.",
            "B. It enforces exclusive, single ownership; it cannot be copied, only moved via `std::move()`.",
            "C. It automatically frees memory only when program execution finishes.",
            "D. It converts heap allocations into static stack memory."
        ]),
        "correct_answer": "B. It enforces exclusive, single ownership; it cannot be copied, only moved via `std::move()`.",
        "explanation": "`std::unique_ptr` represents strict sole ownership of dynamic memory. Its copy constructor is deleted; ownership transfer uses `std::move()`.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Modern C++: shared_ptr",
        "difficulty": 2,
        "statement": "How does `std::shared_ptr` determine when to deallocate the managed heap object?",
        "options": json.dumps([
            "A. Through a background garbage collector thread.",
            "B. When an internal atomic reference count decrements to zero upon shared pointer destruction.",
            "C. When the original variable that constructed the pointer goes out of scope.",
            "D. When `delete` is explicitly called by the programmer."
        ]),
        "correct_answer": "B. When an internal atomic reference count decrements to zero upon shared pointer destruction.",
        "explanation": "`std::shared_ptr` maintains a control block reference counter. When the last owner is destroyed (count reaches 0), the resource is freed.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Inheritance Access Specifiers",
        "difficulty": 2,
        "statement": "When a class inherits publicly (`class Derived : public Base`), how do `public` and `protected` members of `Base` appear in `Derived`?",
        "options": json.dumps([
            "A. All members become private in Derived.",
            "B. Public members remain public, and protected members remain protected in Derived.",
            "C. All members become public in Derived.",
            "D. Protected members are discarded."
        ]),
        "correct_answer": "B. Public members remain public, and protected members remain protected in Derived.",
        "explanation": "Public inheritance preserves access levels: public members remain public, and protected members remain protected.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Exception Handling",
        "difficulty": 1,
        "statement": "Which catch block syntax in C++ acts as a universal catch-all handler for any exception type?",
        "options": json.dumps([
            "A. `catch (std::exception &e)`",
            "B. `catch (...)`",
            "C. `catch (any)`",
            "D. `catch (*)`"
        ]),
        "correct_answer": "B. `catch (...)`",
        "explanation": "The ellipsis `catch (...)` catches any thrown exception regardless of its data type.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "The this Pointer",
        "difficulty": 1,
        "statement": "Inside a non-static member function of class `Car`, what is the type of the `this` pointer?",
        "options": json.dumps([
            "A. `Car&`",
            "B. `Car* const`",
            "C. `void*`",
            "D. `Car**`"
        ]),
        "correct_answer": "B. `Car* const`",
        "explanation": "`this` is a prvalue pointer of type `Car* const` (or `const Car* const` in const methods) pointing to the invoking instance.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Const Member Functions",
        "difficulty": 2,
        "statement": "What guarantee does declaring a member function `void display() const;` provide in C++?",
        "options": json.dumps([
            "A. The function can only be called once.",
            "B. The function promises not to modify any non-mutable member variables of the calling object.",
            "C. The function must return a const value.",
            "D. The function cannot access any member variables."
        ]),
        "correct_answer": "B. The function promises not to modify any non-mutable member variables of the calling object.",
        "explanation": "A const member function treats `this` as `const ClassName*`, preventing modifications to member fields unless marked `mutable`.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "RAII Idiom",
        "difficulty": 2,
        "statement": "What does the RAII (Resource Acquisition Is Initialization) design pattern primarily achieve in C++?",
        "options": json.dumps([
            "A. Binds resource lifetime to object lifetime, guaranteeing automatic cleanup via destructors even during exception unwinding.",
            "B. Eliminates the need for constructors.",
            "C. Compiles C++ code into machine assembly ahead of time.",
            "D. Forces all objects to be initialized with zeros."
        ]),
        "correct_answer": "A. Binds resource lifetime to object lifetime, guaranteeing automatic cleanup via destructors even during exception unwinding.",
        "explanation": "RAII ties resource acquisition to construction and release to destruction, preventing memory and resource leaks.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "STL Iterators",
        "difficulty": 1,
        "statement": "In C++, what does `vec.end()` return for an instance of `std::vector<int>`?",
        "options": json.dumps([
            "A. An iterator pointing to the last element in the vector.",
            "B. An iterator pointing to the theoretical element past-the-end of the vector.",
            "C. The index of the last element.",
            "D. A boolean indicating if the vector is empty."
        ]),
        "correct_answer": "B. An iterator pointing to the theoretical element past-the-end of the vector.",
        "explanation": "`end()` returns an iterator referring to the past-the-end position, serving as an exclusive bound in half-open ranges `[begin, end)`.",
        "marks": 100
    },
    {
        "skill": "cpp",
        "type": "mcq",
        "topic": "Inline Functions",
        "difficulty": 1,
        "statement": "What is the compiler optimization goal of marking a small function with the `inline` keyword in C++?",
        "options": json.dumps([
            "A. To replace the function call directly with the function's machine code body, eliminating function call overhead.",
            "B. To force the function to execute on a dedicated GPU core.",
            "C. To prevent the function from being compiled into the binary.",
            "D. To execute the function asynchronously in the background."
        ]),
        "correct_answer": "A. To replace the function call directly with the function's machine code body, eliminating function call overhead.",
        "explanation": "The `inline` keyword suggests expanding the function code at the call site, eliminating stack push/pop call overhead for small functions.",
        "marks": 100
    }
]


def get_all_questions_data():
    """Return the complete 80 calibrated MCQs."""
    return QUESTION_BANK_DATA
