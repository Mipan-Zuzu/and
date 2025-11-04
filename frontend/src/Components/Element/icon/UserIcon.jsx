const UserIcon = (props) => {
    const {classFrist, classSecond} = props
  return (
    <>
      <a
        href="#"
        className={`flex items-center justify-center ${classFrist} bg-gray-200 rounded-full`}
      >
        <div className="w-20 h-20 rounded-full flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className={`${classSecond} text-gray-800 `}
          >
            <path
              fillRule="evenodd"
              d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 
         1.79-4 4 1.79 4 4 4zm0 1.5c-2.67 0-8 
         1.34-8 4v1.5h16v-1.5c0-2.66-5.33-4-8-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </a>
    </>
  );
};

export default UserIcon;
