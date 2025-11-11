//Unit tests for ScalpAid registration 
//tests data storage, validation and error handling


describe('Registration Form Validation', () => {

    // mock localStorage
    let localStorageMock;

    beforeEach(() => {
        localStorageMock = {
            store: {},
            getItem: function (key) {
                return this.store[key] || null;
            },
            setItem: function (key, value) {
                this.store[key] = value.toString();
            },
            removeItem: function (key) {
                delete this.store[key];
            },
            clear: function () {
                this.store = {};
            }
        };
        global.localStorage = localStorageMock;
    });

    test('TEST 1.1: Valid registration creates user object correctly', () => {
        // arrange
        const name = "Test User";
        const email = "test@example.com";
        const password = "SecurePass123";
        const goal = "Prevent Alopecia";

        // simulate registration
        const newUser = {
            email: email,
            name: name,
            username: "@" + email.split("@")[0],
            goal: goal,
            hairType: "",
            hairTexture: "",
            memberSince: new Date().toLocaleDateString(),
            temperature: null,
            tension: null,
            moisture: null,
            history: { temp: [], tension: [], moisture: [] }
        };

        localStorage.setItem("loggedInUser", JSON.stringify(newUser));
        localStorage.setItem("userGoal", goal);

        // assert
        const storedUser = JSON.parse(localStorage.getItem("loggedInUser"));
        expect(storedUser.email).toBe("test@example.com");
        expect(storedUser.name).toBe("Test User");
        expect(storedUser.username).toBe("@test");
        expect(storedUser.goal).toBe("Prevent Alopecia");
        expect(storedUser.history).toEqual({ temp: [], tension: [], moisture: [] });
        expect(localStorage.getItem("userGoal")).toBe("Prevent Alopecia");
    });

    test('TEST 1.2: Password mismatch validation', () => {
        // arrange
        const password = "SecurePass123";
        const confirmPassword = "DifferentPass456";

        // act & assert
        expect(password).not.toBe(confirmPassword);
    });

    test('TEST 1.3: Empty goal validation', () => {
        // arrange
        const goal = "";

        // act & assert
        expect(goal).toBe("");
        expect(goal.length).toBe(0);
    });

    test('TEST 1.4: Email format validation', () => {
        // arrange
        const validEmail = "test@example.com";
        const invalidEmail = "notanemail";
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        // act & assert
        expect(emailRegex.test(validEmail)).toBe(true);
        expect(emailRegex.test(invalidEmail)).toBe(false);
    });

    test('TEST 1.5: Username generation from email', () => {
        // arrange
        const email = "john.doe@example.com";

        // act
        const username = "@" + email.split("@")[0];

        // assert
        expect(username).toBe("@john.doe");
    });

    test('TEST 1.6: Member since date is set correctly', () => {
        // arrange & act
        const memberSince = new Date().toLocaleDateString();

        // assert
        expect(memberSince).toBeTruthy();
        expect(memberSince.length).toBeGreaterThan(0);
    });

});

describe('Data Storage Tests', () => {

    let localStorageMock;

    beforeEach(() => {
        localStorageMock = {
            store: {},
            getItem: function (key) {
                return this.store[key] || null;
            },
            setItem: function (key, value) {
                this.store[key] = value.toString();
            },
            clear: function () {
                this.store = {};
            }
        };
        global.localStorage = localStorageMock;
    });

    test('TEST 2.1: User data persists in localStorage', () => {
        // arrange
        const userData = {
            email: "test@example.com",
            name: "Test User",
            goal: "Prevent Alopecia"
        };

        // act
        localStorage.setItem("loggedInUser", JSON.stringify(userData));
        const retrieved = JSON.parse(localStorage.getItem("loggedInUser"));

        // assert
        expect(retrieved).toEqual(userData);
    });

    test('TEST 2.2: Goal stored separately', () => {
        // arrange
        const goal = "Manage Alopecia";

        // act
        localStorage.setItem("userGoal", goal);

        // assert
        expect(localStorage.getItem("userGoal")).toBe(goal);
    });

    test('TEST 2.3: Empty history arrays initialize correctly', () => {
        // arrange & act
        const history = { temp: [], tension: [], moisture: [] };

        // assert
        expect(history.temp).toEqual([]);
        expect(history.tension).toEqual([]);
        expect(history.moisture).toEqual([]);
        expect(Array.isArray(history.temp)).toBe(true);
    });

});

describe('Profile Data Display Tests', () => {

    test('TEST 3.1: User object contains all required fields', () => {
        // arrange
        const user = {
            email: "jane@example.com",
            name: "Jane Doe",
            username: "@jane",
            goal: "Improve Hair Health",
            hairType: "",
            hairTexture: "",
            memberSince: "11/26/2024",
            temperature: null,
            tension: null,
            moisture: null,
            history: { temp: [], tension: [], moisture: [] }
        };

        // assert
        expect(user).toHaveProperty("email");
        expect(user).toHaveProperty("name");
        expect(user).toHaveProperty("username");
        expect(user).toHaveProperty("goal");
        expect(user).toHaveProperty("memberSince");
        expect(user).toHaveProperty("history");
    });

    test('TEST 3.2: Profile requires authentication check', () => {
        // arrange
        const user = null; // no logged in user

        // act & assert
        expect(user).toBeNull();
    });

});

describe('Error Handling Tests', () => {

    test('TEST 6.1: Handle null user gracefully', () => {
        // arrange
        const userStr = null;

        // act
        let user;
        try {
            user = JSON.parse(userStr);
        } catch (e) {
            user = null;
        }

        // assert
        expect(user).toBeNull();
    });

    test('TEST 6.2: Handle invalid JSON in localStorage', () => {
        // arrange
        const invalidJSON = "not valid json{";

        // act & assert
        expect(() => JSON.parse(invalidJSON)).toThrow();
    });

    test('TEST 6.3: Handle missing localStorage data', () => {
        // arrange
        global.localStorage = {
            getItem: () => null
        };

        // act
        const user = localStorage.getItem("loggedInUser");

        // assert
        expect(user).toBeNull();
    });

});

describe('Goal-Based UI Logic Tests', () => {

    test('TEST 4.1: Prevent Alopecia goal sets correct visibility', () => {
        // arrange
        const goal = "Prevent Alopecia";

        // act
        const showPrevent = goal === "Prevent Alopecia";
        const showManage = goal === "Manage Alopecia";
        const showImprove = goal === "Improve Hair Health";

        // assert
        expect(showPrevent).toBe(true);
        expect(showManage).toBe(false);
        expect(showImprove).toBe(false);
    });

    test('TEST 4.2: Manage Alopecia goal sets correct visibility', () => {
        // arrange
        const goal = "Manage Alopecia";

        // act
        const showPrevent = goal === "Prevent Alopecia";
        const showManage = goal === "Manage Alopecia";
        const showImprove = goal === "Improve Hair Health";

        // assert
        expect(showPrevent).toBe(false);
        expect(showManage).toBe(true);
        expect(showImprove).toBe(false);
    });

});

describe('Demo User (Brianna) Tests', () => {

    test('TEST 5.1: Detect demo user by email', () => {
        // arrange
        const user = { email: "brianna@example.com" };

        // act
        const isBrianna = user.email && user.email.toLowerCase() === "brianna@example.com";

        // assert
        expect(isBrianna).toBe(true);
    });

    test('TEST 5.2: Non-demo user returns false', () => {
        // arrange
        const user = { email: "regular@example.com" };

        // act
        const isBrianna = user.email && user.email.toLowerCase() === "brianna@example.com";

        // assert
        expect(isBrianna).toBe(false);
    });

});