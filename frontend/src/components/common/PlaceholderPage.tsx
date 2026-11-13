
interface PlaceholderPageProps {
  title: string;
  description: string;
}

export default function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <main>
      <h1>{title}</h1>
      <p>{description}</p>
    </main>
  );
}
