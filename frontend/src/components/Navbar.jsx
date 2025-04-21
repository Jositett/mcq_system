import { Fragment } from "react";
import { Disclosure, Menu, Transition } from "@headlessui/react";
import { Bars3Icon, XMarkIcon, SunIcon, MoonIcon, BellIcon } from "@heroicons/react/24/outline";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { logout } from "../features/authSlice";
import { toggleTheme } from "../features/themeSlice";
import { useToast } from "./ToastContext";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const showToast = useToast();
  
  // Get auth state from Redux
  const { isAuthenticated, user, role } = useSelector(state => state.auth);
  
  // Get theme from Redux
  const { theme } = useSelector(state => state.theme);
  
  const navigation = [
    { name: "Dashboard", to: "/dashboard", show: isAuthenticated },
    { name: "Admin", to: "/admin", show: role === "admin" },
    { name: "Instructor", to: "/instructor", show: role === "instructor" || role === "admin" },
    { name: "Attendance", to: "/attendance/checkin", show: isAuthenticated && role === "student" },
  ];

  const handleLogout = () => {
    dispatch(logout());
    showToast('Logged out successfully', 'success');
    navigate('/');
  };
  
  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };
  
  // Determine if the current path matches a navigation item
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <Disclosure as="nav" className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-200">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 justify-between items-center">
              <div className="flex items-center">
                <Link to="/" className="font-bold text-xl text-blue-600 dark:text-blue-400 transition-colors duration-200">MCQ System</Link>
                <div className="hidden md:block ml-10 space-x-1">
                  {navigation.filter(n => n.show).map((item) => (
                    <Link
                      key={item.name}
                      to={item.to}
                      className={classNames(
                        isActive(item.to)
                          ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                          : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700",
                        "px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                      )}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Theme toggle button */}
                <button
                  onClick={handleThemeToggle}
                  className="rounded-md p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                  aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                >
                  {theme === 'dark' ? (
                    <SunIcon className="h-5 w-5" aria-hidden="true" />
                  ) : (
                    <MoonIcon className="h-5 w-5" aria-hidden="true" />
                  )}
                </button>
                
                {/* Notifications button - only show when authenticated */}
                {isAuthenticated && (
                  <Link
                    to="/notifications"
                    className="rounded-md p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                    aria-label="Notifications"
                  >
                    <BellIcon className="h-5 w-5" aria-hidden="true" />
                  </Link>
                )}
                
                {isAuthenticated ? (
                  <Menu as="div" className="relative">
                    <div>
                      <Menu.Button className="flex rounded-full bg-gray-100 dark:bg-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200">
                        <span className="sr-only">Open user menu</span>
                        {user?.profile_picture ? (
                          <img
                            className="h-8 w-8 rounded-full object-cover"
                            src={user.profile_picture}
                            alt={user.full_name || user.username}
                          />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center font-bold text-blue-800 dark:text-blue-200 transition-colors duration-200">
                            {user?.full_name?.[0] || user?.username?.[0] || "U"}
                          </div>
                        )}
                      </Menu.Button>
                    </div>
                    <Transition
                      as={Fragment}
                      enter="transition ease-out duration-100"
                      enterFrom="transform opacity-0 scale-95"
                      enterTo="transform opacity-100 scale-100"
                      leave="transition ease-in duration-75"
                      leaveFrom="transform opacity-100 scale-100"
                      leaveTo="transform opacity-0 scale-95"
                    >
                      <Menu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition-colors duration-200">
                        <div className="px-4 py-2 border-b border-gray-100 dark:border-gray-700">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.full_name || user?.username}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                        </div>
                        
                        <Menu.Item>
                          {({ active }) => (
                            <Link
                              to="/profile"
                              className={classNames(
                                active ? "bg-gray-100 dark:bg-gray-700" : "",
                                "block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 transition-colors duration-200"
                              )}
                            >
                              Your Profile
                            </Link>
                          )}
                        </Menu.Item>
                        
                        <Menu.Item>
                          {({ active }) => (
                            <button
                              className={classNames(
                                active ? "bg-gray-100 dark:bg-gray-700" : "",
                                "block w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 text-left transition-colors duration-200"
                              )}
                              onClick={handleLogout}
                            >
                              Sign out
                            </button>
                          )}
                        </Menu.Item>
                      </Menu.Items>
                    </Transition>
                  </Menu>
                ) : (
                  <div className="space-x-2">
                    <Link 
                      to="/login" 
                      className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors duration-200"
                    >
                      Sign in
                    </Link>
                    <Link 
                      to="/register" 
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                    >
                      Sign up
                    </Link>
                  </div>
                )}
              </div>
              
              <div className="-mr-2 flex md:hidden">
                <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>
          
          <Disclosure.Panel className="md:hidden">
            <div className="space-y-1 px-2 pt-2 pb-3">
              {navigation.filter(n => n.show).map((item) => (
                <Link
                  key={item.name}
                  to={item.to}
                  className={classNames(
                    isActive(item.to)
                      ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                      : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700",
                    "block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
                  )}
                >
                  {item.name}
                </Link>
              ))}
              
              {/* Mobile theme toggle */}
              <button
                onClick={handleThemeToggle}
                className="flex w-full items-center px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors duration-200"
              >
                {theme === 'dark' ? (
                  <>
                    <SunIcon className="h-5 w-5 mr-2" aria-hidden="true" />
                    <span>Light Mode</span>
                  </>
                ) : (
                  <>
                    <MoonIcon className="h-5 w-5 mr-2" aria-hidden="true" />
                    <span>Dark Mode</span>
                  </>
                )}
              </button>
            </div>
            
            {isAuthenticated && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4 pb-3">
                <div className="flex items-center px-5">
                  {user?.profile_picture ? (
                    <img
                      className="h-10 w-10 rounded-full object-cover"
                      src={user.profile_picture}
                      alt={user.full_name || user.username}
                    />
                  ) : (
                    <div className="h-10 w-10 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center font-bold text-blue-800 dark:text-blue-200 transition-colors duration-200">
                      {user?.full_name?.[0] || user?.username?.[0] || "U"}
                    </div>
                  )}
                  <div className="ml-3">
                    <div className="text-base font-medium text-gray-800 dark:text-white">{user?.full_name || user?.username}</div>
                    <div className="text-sm font-medium text-gray-500 dark:text-gray-400">{user?.email}</div>
                  </div>
                </div>
                <div className="mt-3 space-y-1 px-2">
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    Your Profile
                  </Link>
                  <Link
                    to="/notifications"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    Notifications
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                  >
                    Sign out
                  </button>
                </div>
              </div>
            )}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
