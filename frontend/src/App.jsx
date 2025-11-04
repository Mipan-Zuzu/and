import "./index.css";
import Navbar from "./Components/navbar/index";
import Items from "./Components/Items";
import UserIcon from "./Components/Element/icon/UserIcon";
import Friend from "./Components/Friend"
import AlgoritmaFriend from "./Components/AlgoritmaFriend"

function App() {
  return (
    <div className="">
      <Navbar />
      <Items />
      <VibesTitle />
      <DaftarText>Teman anda di &and</DaftarText>
      <Friend />
      <DaftarText>Disarankan untuk anda</DaftarText>
      <AlgoritmaFriend/>
    </div>
  );
}

const DaftarText = (props) => {
  const {children} = props
  return (
    <div className="px-5 mt-5 lg:px-10">
          <h1 className="text-lg font-bold">
            {children}
          </h1>
      </div>
  )
}

const VibesTitle = () => {
  return (
    <div className="flex items-center  p-3 sm:p-4 md:p-5 mt-4 mx-3 sm:mx-5 font-mono">
      <UserIcon
        className="w-6 h-6 sm:w-7 sm:h-7 text-gray-400"
        classFrist={"w-10 h-10"}
        classSecond={"w-10 w-10"}
      />
      <h1 className="mx-3 sm:mx-5 text-gray-400 text-base sm:text-sm md:text-lg font-light">
        Bagaimana hari mu ?
      </h1>
    </div>
  );
};

export default App;
