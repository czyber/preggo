-- Enable RLS on media_items table
ALTER TABLE media_items ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can insert their own media" ON media_items;
DROP POLICY IF EXISTS "Users can view media from accessible posts" ON media_items;
DROP POLICY IF EXISTS "Users can update their own media" ON media_items;
DROP POLICY IF EXISTS "Users can delete their own media" ON media_items;

-- Allow authenticated users to insert their own media
CREATE POLICY "Users can insert their own media" 
ON media_items FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid()::text = uploaded_by);

-- Allow users to view media from posts they can access
CREATE POLICY "Users can view media from accessible posts" 
ON media_items FOR SELECT 
TO authenticated 
USING (
    -- User uploaded the media
    auth.uid()::text = uploaded_by
    OR
    -- Media is attached to a post (we'll check post access separately)
    post_id IS NOT NULL
    OR
    -- Media is not yet attached to any post but was uploaded by the user
    (post_id IS NULL AND auth.uid()::text = uploaded_by)
);

-- Allow users to update their own media
CREATE POLICY "Users can update their own media" 
ON media_items FOR UPDATE 
TO authenticated 
USING (auth.uid()::text = uploaded_by)
WITH CHECK (auth.uid()::text = uploaded_by);

-- Allow users to delete their own media
CREATE POLICY "Users can delete their own media" 
ON media_items FOR DELETE 
TO authenticated 
USING (auth.uid()::text = uploaded_by);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_media_items_uploaded_by ON media_items(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_media_items_post_id ON media_items(post_id);
CREATE INDEX IF NOT EXISTS idx_media_items_created_at ON media_items(created_at DESC);