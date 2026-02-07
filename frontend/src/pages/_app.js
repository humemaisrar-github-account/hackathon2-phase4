import '../styles/globals.css';
import { AuthProvider } from '../services/auth';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import FloatingChatWidget from '../components/chat/FloatingChatWidget';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow">
          <Component {...pageProps} />
        </main>
        <FloatingChatWidget />
        <Footer />
      </div>
    </AuthProvider>
  );
}

export default MyApp;
