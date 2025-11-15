import UserIcon from "../../Element/icon/UserIcon";
const Login = () => {
  return (
    <form action="">
      <div className="min-h-screen gap-52 flex justify-self-center items-center">
      <div className="flex flex-col">
        <div className="flex">
          <img src="../../../../public/images/&.png" alt="logo" width={80} />
          <span className="text-5xl mt-3">And</span>
        </div>
        <div>
          <h1 className="text-2xl">Intrested to Login and register and</h1>
          <p>Conect your study and friend whole world</p>
        </div>
        <div className="mt-2 flex gap-2">
          <p className="font-light">&and © 2025 </p>
          <p className="font-light">| Indonesia</p>
        </div>
        <div className="mt-5 flex gap-3">
          <div className="p-10 rounded-lg w-36 h-40 border border-gray-600 hover:border-white hover:scale-105 duration-300">
              <UserIcon classFrist={'w-15 h-15'} classSecond={'w-15 w-15'}/>
          <div className="mt-2">
            <h1 className="font-bold">@Mipa</h1>
          </div>
          </div>
          <div className="p-10 rounded-lg w-36 h-40 border border-gray-600 hover:border-white hover:scale-105 duration-300">
              <UserIcon classFrist={'w-15 h-15'} classSecond={'w-15 w-15'}/>
          <div className="mt-2">
            <h1 className="font-bold">@Rusdi</h1>
          </div>
          </div>
        </div>
      </div>
        <div className="flex flex-col font-mono">
          <Label label={"email"} type={"email"} placeholder={"Example@mail.com "}>Email</Label>
          <div className="mt-3">
            <Label label={"password"} type={"password"} placeholder={"*******"}>Password</Label>
          </div>
          <p className="text-gray-500 mt-4 mb-2 text-sm font-light">
            dont have any account{" "}
            <a href="#" className="text-blue-400">
              signUp
            </a>
          </p>
          <button
            className="bg-white text-black rounded-lg p-1 font-mono hover:bg-black border border-white duration-300 hover:text-white cursor-pointer"
            type="sumbit"
          >
            Sign in
          </button>
        </div>
      </div>
    </form>
  );
};

const Label = (props) => {
  const {children, label, type, placeholder} = props
  return (
    <label htmlFor={label}>
      <h1>{children}</h1>
      <input
        type={type}
        className="border mt-2 border-gray-500 rounded-sm h-10 w-70 p-4"
        placeholder={placeholder}
        required
      />
    </label>
  );
};

export default Login;
